<script lang="ts">
  import '../styles/global.css';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import UploadQueue from '$lib/components/UploadQueue.svelte';
  import ClipboardPrompt from '$lib/components/ClipboardPrompt.svelte';
  import Auth from '$lib/components/Auth.svelte';
  import DevBadge from '$lib/components/DevBadge.svelte';
  import { page } from '$app/stores';
  import type { Snippet } from 'svelte';
  import { onMount } from 'svelte';
  import { initUploadManager, addFileUpload } from '$lib/stores/upload.svelte';
  import { initClipboardManager } from '$lib/stores/clipboard.svelte';
  import { listen } from '@tauri-apps/api/event';
  import { invoke } from '@tauri-apps/api/core';
  import { onOpenUrl } from '@tauri-apps/plugin-deep-link';
  import { getProfile } from '$lib/api';

  type Props = { children: Snippet };
  let { children }: Props = $props();

  let isAuthenticated = $state(false);
  let isChecking = $state(true);
  const isOverlayRoute = $derived($page.url.pathname.startsWith('/overlay'));

  onMount(async () => {
    if (isOverlayRoute) {
        isChecking = false;
        return;
    }

    try {
        await getProfile();
        isAuthenticated = true;
    } catch (e) {
        isAuthenticated = false;
    } finally {
        isChecking = false;
    }

    initUploadManager();
    initClipboardManager();
    invoke('register_context_menu').catch((error) => {
        console.warn('File Explorer integration was not registered', error);
    });

    // Check for updates automatically in the background
    invoke('check_update').then((hasUpdate) => {
        if (hasUpdate) {
            console.log("An update is available and ready to install.");
        }
    }).catch((error) => {
        console.warn('Update check failed on startup', error);
    });

    // Listen to Tauri window drops
    listen('tauri://drop', (event: any) => {
        const paths = event.payload.paths as string[];
        if (paths && paths.length > 0) {
            paths.forEach(p => addFileUpload(p));
        }
    });

    // Listen for deep link authentication (Google OAuth)
    try {
        await onOpenUrl(async (urls) => {
            for (const urlStr of urls) {
                if (urlStr.includes('snaply://auth')) {
                    try {
                        const url = new URL(urlStr);
                        const token = url.searchParams.get('token');
                        if (token) {
                            await invoke('set_auth_token', { token });
                            await getProfile(); // verify the token works
                            isAuthenticated = true;
                        }
                    } catch (e) {
                        console.error('Failed to parse deep link token', e);
                    }
                }
            }
        });
    } catch (e) {
        console.warn('Deep link plugin not fully initialized in this env', e);
    }
  });
</script>

{#if isOverlayRoute}
  {@render children()}
{:else if isChecking}
  <div class="app-shell" style="justify-content: center; align-items: center;">
    <div style="color: var(--text-secondary);">Loading...</div>
  </div>
{:else if !isAuthenticated}
  <Auth onLogin={() => isAuthenticated = true} />
{:else}
  <div class="app-shell">
    <Sidebar />
    <main class="app-content">
      {@render children()}
    </main>
  </div>

  <UploadQueue />
  <ClipboardPrompt />
{/if}

<DevBadge />

<style>
  .app-shell {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }

  .app-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--space-6) var(--space-8);
    min-width: 0;
  }

  .app-content :global(.page-header),
  .app-content :global(.page-content) {
    width: min(100%, 1000px);
    margin-left: auto;
    margin-right: auto;
  }
</style>
