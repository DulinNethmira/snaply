import { listen } from '@tauri-apps/api/event';
import { invoke } from '@tauri-apps/api/core';
import { requestUpload, completeUpload } from '$lib/api';
import { getShareUrl } from '$lib/config';

export type UploadState = 'Queued' | 'Preparing' | 'Uploading' | 'Processing' | 'Complete' | 'Failed' | 'Cancelled';

export interface UploadTask {
    id: string;
    path?: string;
    capture_key?: string;
    filename: string;
    state: UploadState;
    uploadedBytes: number;
    totalBytes: number;
    speedBps: number;
    etaSeconds: number;
}

export const uploadState = $state({
    queue: [] as UploadTask[]
});

let _initialized = false;
let _lastProgress: Record<string, number> = {}; // for speed calc

export function initUploadManager() {
    if (_initialized) return;
    _initialized = true;

    listen('upload-progress', (event: any) => {
        const { id, uploaded, total } = event.payload;
        const task = uploadState.queue.find(t => t.id === id);
        if (task && task.state === 'Uploading') {
            const now = Date.now();
            const lastTime = _lastProgress[id + '_time'] || now - 100;
            const lastUploaded = _lastProgress[id + '_bytes'] || 0;
            
            const timeDiff = (now - lastTime) / 1000;
            const bytesDiff = uploaded - lastUploaded;
            
            if (timeDiff > 0.5) {
                task.speedBps = bytesDiff / timeDiff;
                _lastProgress[id + '_time'] = now;
                _lastProgress[id + '_bytes'] = uploaded;
            }

            task.uploadedBytes = uploaded;
            task.totalBytes = total;
            if (task.speedBps > 0) {
                task.etaSeconds = (total - uploaded) / task.speedBps;
            }
        }
    });

    listen('file-shared', (event: any) => {
        const args = event.payload as string[];
        if (args && args.length > 0) {
            args.forEach(arg => addFileUpload(arg));
        }
    });
}

function getMimeType(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    const mimes: Record<string, string> = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'mp4': 'video/mp4',
        'txt': 'text/plain',
        'pdf': 'application/pdf',
        'zip': 'application/zip',
    };
    return mimes[ext || ''] || 'application/octet-stream';
}

export async function addFileUpload(filePath: string) {
    const filename = filePath.split('\\').pop() || filePath.split('/').pop() || 'Unknown';
    const id = crypto.randomUUID();
    
    uploadState.queue.push({
        id,
        path: filePath,
        filename,
        state: 'Preparing',
        uploadedBytes: 0,
        totalBytes: 0,
        speedBps: 0,
        etaSeconds: 0,
    });

    const task = uploadState.queue.find(t => t.id === id)!;
    
    try {
        // Assume file size is unknown until we try to upload, or we can get it via a Rust command.
        // But let's just pass a dummy size to requestUpload (backend can enforce quotas later).
        // For accurate size, we should get it from Rust. Let's use a placeholder of 1MB for the request quota check.
        // The real size will be streamed.
        const req = await requestUpload(filename, 1024 * 1024, getMimeType(filename));
        
        task.state = 'Uploading';
        
        await invoke('upload_file_to_r2', { 
            id, 
            path: filePath, 
            url: req.upload_url,
            mimeType: getMimeType(filename)
        });
        
        task.state = 'Processing';
        const comp = await completeUpload(req.upload_id);
        
        task.state = 'Complete';
        task.uploadedBytes = task.totalBytes; // ensure UI shows 100%
        
        addHistory(task, comp.token);
        
    } catch (e) {
        console.error("Upload failed", e);
        task.state = e === 'Upload cancelled' ? 'Cancelled' : 'Failed';
    } finally {
        delete _lastProgress[id + '_time'];
        delete _lastProgress[id + '_bytes'];
    }
}

export async function addBrowserFileUpload(file: File) {
    const id = crypto.randomUUID();
    const filename = file.name || 'upload.bin';

    uploadState.queue.push({
        id,
        filename,
        state: 'Preparing',
        uploadedBytes: 0,
        totalBytes: file.size,
        speedBps: 0,
        etaSeconds: 0,
    });

    const task = uploadState.queue.find(t => t.id === id)!;

    try {
        const req = await requestUpload(filename, file.size || 1, file.type || getMimeType(filename));
        task.state = 'Uploading';

        const startedAt = Date.now();
        const response = await fetch(req.upload_url, {
            method: 'PUT',
            headers: { 'Content-Type': file.type || getMimeType(filename) },
            body: file,
        });

        if (!response.ok) {
            throw new Error(`Upload failed with status ${response.status}`);
        }

        task.uploadedBytes = file.size;
        task.totalBytes = file.size;
        const elapsedSeconds = Math.max((Date.now() - startedAt) / 1000, 0.1);
        task.speedBps = file.size / elapsedSeconds;
        task.etaSeconds = 0;

        task.state = 'Processing';
        const comp = await completeUpload(req.upload_id);

        task.state = 'Complete';
        addHistory(task, comp.token);
    } catch (e) {
        console.error('Upload failed', e);
        task.state = 'Failed';
    } finally {
        delete _lastProgress[id + '_time'];
        delete _lastProgress[id + '_bytes'];
    }
}

export async function addMemoryUpload(captureKey: string, filename: string, mimeType: string, isText: boolean = false) {
    const id = crypto.randomUUID();
    
    uploadState.queue.push({
        id,
        capture_key: captureKey,
        filename,
        state: 'Preparing',
        uploadedBytes: 0,
        totalBytes: 0,
        speedBps: 0,
        etaSeconds: 0,
    });

    const task = uploadState.queue.find(t => t.id === id)!;
    
    try {
        const req = await requestUpload(filename, 1024, mimeType);
        
        task.state = 'Uploading';
        
        await invoke('upload_bytes_to_r2', { 
            id, 
            captureKey, 
            url: req.upload_url,
            mimeType
        });
        
        task.state = 'Processing';
        const comp = await completeUpload(req.upload_id);
        
        task.state = 'Complete';
        
        addHistory(task, comp.token);
        
    } catch (e) {
        console.error("Upload failed", e);
        task.state = 'Failed';
    } finally {
        delete _lastProgress[id + '_time'];
        delete _lastProgress[id + '_bytes'];
    }
}

export function cancelUpload(id: string) {
    const task = uploadState.queue.find(t => t.id === id);
    if (task && task.state === 'Uploading') {
        task.state = 'Cancelled';
        invoke('cancel_upload', { id });
    }
}

// Simple local history tracking (temporary until dashboard reloads from API)
export const historyState = $state({
    items: [] as any[]
});

function formatBytes(bytes: number) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function addHistory(task: UploadTask, token: string) {
    const url = `${getShareUrl()}/s/${token}`;
    
    // Copy URL automatically to clipboard
    navigator.clipboard.writeText(url);
    
    // Notify via OS
    new Notification("Upload Complete", {
        body: `Link copied to clipboard: ${url}`
    });
    
    historyState.items.unshift({
        id: task.id,
        filename: task.filename,
        size: formatBytes(task.totalBytes),
        type: 'file',
        views: 0,
        created_at: 'Just now',
        url: url
    });
}
