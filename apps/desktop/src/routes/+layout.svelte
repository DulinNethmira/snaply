<script lang="ts">
  import '../styles/global.css';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import UploadQueue from '$lib/components/UploadQueue.svelte';
  import ClipboardPrompt from '$lib/components/ClipboardPrompt.svelte';
  import Auth from '$lib/components/Auth.svelte';
  import DevBadge from '$lib/components/DevBadge.svelte';
  import type { Snippet } from 'svelte';
  import { onMount } from 'svelte';
  import { initUploadManager, addFileUpload } from '$lib/stores/upload.svelte';
  import { initClipboardManager } from '$lib/stores/clipboard.svelte';
  import { listen } from '@tauri-apps/api/event';
  import { getProfile } from '$lib/api';

  type Props = { children: Snippet };
  let { children }: Props = $props();

  let isAuthenticated = $state(false);
  let isChecking = $state(true);

  onMount(async () => {
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

    // Listen to Tauri window drops
    listen('tauri://drop', (event: any) => {
        const paths = event.payload.paths as string[];
        if (paths && paths.length > 0) {
            paths.forEach(p => addFileUpload(p));
        }
    });
  });
</script>

{#if isChecking}
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
</style>
