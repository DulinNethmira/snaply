import type { ShareItem, Device, UsageStats, SettingsData } from '$lib/types';

export const mockShares: ShareItem[] = [
  {
    id: '1',
    filename: 'dashboard-redesign.png',
    type: 'screenshot',
    size: 2_458_624,
    url: 'https://snply.to/abc123',
    createdAt: new Date(Date.now() - 1000 * 60 * 12),
    expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24),
    views: 14,
    status: 'active'
  },
  {
    id: '2',
    filename: 'api-response.json',
    type: 'file',
    size: 4_096,
    url: 'https://snply.to/def456',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
    expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 6),
    views: 3,
    status: 'active'
  },
  {
    id: '3',
    filename: 'error-log-output.txt',
    type: 'clipboard',
    size: 1_287,
    url: 'https://snply.to/ghi789',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 5),
    expiresAt: null,
    views: 27,
    status: 'active'
  },
  {
    id: '4',
    filename: 'component-library.fig',
    type: 'file',
    size: 18_743_296,
    url: 'https://snply.to/jkl012',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24),
    expiresAt: new Date(Date.now() - 1000 * 60 * 60),
    views: 42,
    status: 'expired'
  },
  {
    id: '5',
    filename: 'bug-repro-capture.png',
    type: 'screenshot',
    size: 891_204,
    url: 'https://snply.to/mno345',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 48),
    expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 120),
    views: 8,
    status: 'active'
  }
];

export const mockDevices: Device[] = [
  {
    id: '1',
    name: 'Main Workstation',
    type: 'desktop',
    lastSeen: new Date(),
    isOnline: true,
    os: 'Windows 11'
  },
  {
    id: '2',
    name: 'MacBook Pro',
    type: 'laptop',
    lastSeen: new Date(Date.now() - 1000 * 60 * 30),
    isOnline: false,
    os: 'macOS 15'
  }
];

export const mockUsage: UsageStats = {
  totalShares: 147,
  storageUsed: 524_288_000,
  storageLimit: 5_368_709_120,
  activeLinks: 12,
  sharesToday: 3,
  viewsToday: 48
};

export const mockSettings: SettingsData = {
  general: {
    launchAtStartup: true,
    minimizeToTray: true,
    notifications: true
  },
  shortcuts: {
    captureScreen: 'Ctrl+Shift+S',
    captureArea: 'Ctrl+Shift+A',
    uploadClipboard: 'Ctrl+Shift+V'
  },
  appearance: {
    theme: 'dark',
    accentColor: '#7C6DF7',
    compactMode: false
  },
  uploads: {
    autoUpload: true,
    defaultExpiry: '24h',
    quality: 'original',
    maxFileSize: 104_857_600
  },
  privacy: {
    stripMetadata: true,
    requirePassword: false,
    defaultPassword: ''
  }
};

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export function formatRelativeTime(date: Date): string {
  const now = Date.now();
  const diff = now - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

export function formatExpiry(date: Date | null): string {
  if (!date) return 'Never';
  const now = Date.now();
  const diff = date.getTime() - now;
  if (diff <= 0) return 'Expired';
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (hours < 1) return `${Math.floor(diff / 60000)}m left`;
  if (hours < 24) return `${hours}h left`;
  return `${days}d left`;
}

export function getGreeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 18) return 'Good afternoon';
  return 'Good evening';
}

export function getFileIcon(type: ShareItem['type']): string {
  switch (type) {
    case 'screenshot': return 'image';
    case 'image': return 'image';
    case 'clipboard': return 'clipboard';
    case 'file': return 'file';
  }
}
