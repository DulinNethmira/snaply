export interface ShareItem {
  id: string;
  filename: string;
  type: 'image' | 'file' | 'screenshot' | 'clipboard';
  size: number;
  url: string;
  createdAt: Date;
  expiresAt: Date | null;
  views: number;
  status: 'active' | 'expired' | 'deleted';
}

export interface Device {
  id: string;
  name: string;
  type: 'desktop' | 'laptop' | 'phone' | 'tablet';
  lastSeen: Date;
  isOnline: boolean;
  os: string;
}

export interface UsageStats {
  totalShares: number;
  storageUsed: number;
  storageLimit: number;
  activeLinks: number;
  sharesToday: number;
  viewsToday: number;
}

export interface SettingsData {
  general: {
    launchAtStartup: boolean;
    minimizeToTray: boolean;
    notifications: boolean;
  };
  shortcuts: {
    captureScreen: string;
    captureArea: string;
    uploadClipboard: string;
  };
  appearance: {
    theme: 'dark' | 'light' | 'system';
    accentColor: string;
    compactMode: boolean;
  };
  uploads: {
    autoUpload: boolean;
    defaultExpiry: '1h' | '24h' | '7d' | '30d' | 'never';
    quality: 'original' | 'high' | 'medium';
    maxFileSize: number;
  };
  privacy: {
    stripMetadata: boolean;
    requirePassword: boolean;
    defaultPassword: string;
  };
}

export type UploadState = 'idle' | 'hover' | 'dragging' | 'uploading' | 'processing' | 'success' | 'failed';

export type NavItem = {
  id: string;
  label: string;
  path: string;
  icon: string;
};
