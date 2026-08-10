import { listen } from '@tauri-apps/api/event';

export type ClipboardType = 'image' | 'text' | 'url' | null;

export const clipboardState = $state({
    detectedType: null as ClipboardType,
    showPrompt: false,
});

let _initialized = false;

export function initClipboardManager() {
    if (_initialized) return;
    _initialized = true;

    listen('clipboard-detected', (event: any) => {
        const type = event.payload as ClipboardType;
        clipboardState.detectedType = type;
        clipboardState.showPrompt = true;
    });
}
