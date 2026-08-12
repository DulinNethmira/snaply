<script lang="ts">
  import ShareItemComponent from '$lib/components/ShareItem.svelte';
  import EmptyState from '$lib/components/EmptyState.svelte';
  import { historyState } from '$lib/stores/upload.svelte';
  import { getRecentShares } from '$lib/api';
  import { invoke } from '@tauri-apps/api/core';
  import { onMount } from 'svelte';

  let apiShares: any[] = $state([]);

  onMount(async () => {
      try {
          apiShares = await getRecentShares();
      } catch (e) {
          console.error(e);
      }
  });

  const allShares = $derived([...historyState.items, ...apiShares].filter((v, i, a) => a.findIndex(t => (t.id === v.id)) === i));
  const hasShares = $derived(allShares.length > 0);
</script>

<div class="page-header">
  <h1 class="page-title">Recent Shares</h1>
  <p class="page-subtitle">Manage and track your active links.</p>
</div>

<div class="page-content">
  {#if hasShares}
    <div class="shares-list">
      {#each allShares as item (item.id)}
        <ShareItemComponent {item} />
      {/each}
    </div>
  {:else}
    <div class="empty-container">
      <EmptyState
        title="No shares yet."
        description="Your first screenshot can be shared in seconds. Drop a file to get started."
        actionLabel="Capture Screenshot"
        onaction={() => invoke('start_capture')}
      />
    </div>
  {/if}
</div>

<style>
  .page-header {
    margin-bottom: var(--space-8);
  }

  .page-title {
    font-size: var(--text-2xl);
    letter-spacing: -0.02em;
    margin-bottom: var(--space-1);
  }

  .page-subtitle {
    color: var(--text-muted);
    font-size: var(--text-md);
  }

  .page-content {
    max-width: 800px;
  }

  .shares-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: var(--space-2);
  }

  .empty-container {
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: var(--radius-xl);
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>
