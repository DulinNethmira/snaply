import { invoke } from '@tauri-apps/api/core';

export const API_URL = 'http://127.0.0.1:8000/api/v1';

async function getToken(): Promise<string | null> {
    try {
        const token = await invoke('get_auth_token');
        return token as string | null;
    } catch {
        return null;
    }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = await getToken();
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...((options.headers as Record<string, string>) || {}),
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!res.ok) {
        let errorMsg = `Error: ${res.status}`;
        try {
            const errBody = await res.json();
            if (errBody.detail) {
                errorMsg = errBody.detail;
            }
        } catch {}
        throw new Error(errorMsg);
    }

    return res.json();
}

// ----------------------------------------------------
// Authentication
// ----------------------------------------------------

export async function login(email: string, password: string) {
    const res = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
        let msg = 'Login failed';
        try {
            const data = await res.json();
            if (data.detail) msg = data.detail;
        } catch {}
        throw new Error(msg);
    }

    const data = await res.json();
    await invoke('set_auth_token', { token: data.access_token });
    return data;
}

export async function register(username: string, password: string) {
    const res = await request<any>('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ email: username, password }),
    });
    return res;
}

export async function logout() {
    try {
        await invoke('delete_auth_token');
    } catch (e) {
        console.error(e);
    }
}

// ----------------------------------------------------
// Uploads
// ----------------------------------------------------

export interface UploadRequestResponse {
    upload_id: string;
    upload_url: string;
}

export interface CompleteUploadResponse {
    id: string;
    token: string;
    expires_at: string | null;
}

export async function requestUpload(filename: string, size: number, mime_type: string): Promise<UploadRequestResponse> {
    return request<UploadRequestResponse>('/uploads/request', {
        method: 'POST',
        body: JSON.stringify({ filename, size, mime_type }),
    });
}

export async function completeUpload(upload_id: string): Promise<CompleteUploadResponse> {
    return request<CompleteUploadResponse>(`/uploads/${upload_id}/complete`, {
        method: 'POST',
    });
}

// ----------------------------------------------------
// User & Shares
// ----------------------------------------------------

export async function getProfile() {
    return request<any>('/users/me');
}

export async function getRecentShares() {
    const shares = await request<any[]>('/users/me/shares');
    return shares.map((share) => ({
        ...share,
        createdAt: new Date(share.createdAt),
        expiresAt: share.expiresAt ? new Date(share.expiresAt) : null,
    }));
}

export async function getUsageStats() {
    const profile = await getProfile();
    let shares: any[] = [];
    try {
        shares = await getRecentShares();
    } catch {
        // shares not critical for usage stats
    }

    const activeShares = shares.filter((share) => share.status === 'active');
    const today = new Date().toDateString();

    return {
        totalShares: shares.length,
        storageUsed: profile.storage_used ?? 0,
        storageLimit: profile.storage_limit ?? 0,
        activeLinks: activeShares.length,
        sharesToday: shares.filter((share) => share.createdAt?.toDateString?.() === today).length,
        viewsToday: activeShares.reduce((sum: number, share: any) => sum + (share.views ?? 0), 0),
        monthlyUploads: profile.monthly_uploads ?? 0,
        monthlyLimit: profile.monthly_limit ?? 0,
    };
}

export async function deleteShare(shareId: string) {
    return request(`/shares/${shareId}`, {
        method: 'DELETE',
    });
}
