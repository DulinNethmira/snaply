<script lang="ts">
  import { formatBytes } from '$lib/data/mock';
  import StatCard from '$lib/components/StatCard.svelte';
  import { getUsageStats } from '$lib/api';
  import { onMount } from 'svelte';

  let usage = $state({
    totalShares: 0,
    storageUsed: 0,
    storageLimit: 0,
    activeLinks: 0,
    sharesToday: 0,
    viewsToday: 0,
  });

  let isLoading = $state(true);
  let loadError = $state('');

  const storagePercentage = $derived(
    usage.storageLimit > 0 ? Math.min(100, (usage.storageUsed / usage.storageLimit) * 100) : 0
  );

  onMount(async () => {
    try {
      usage = await getUsageStats();
    } catch (e: any) {
      loadError = e.message || 'Unable to load usage';
    } finally {
      isLoading = false;
    }
  });
</script>

<div class="page-header">
  <h1 class="page-title">Usage & Storage</h1>
  <p class="page-subtitle">Keep track of your cloud storage and sharing limits.</p>
</div>

<div class="page-content">
  {#if loadError}
    <div class="status-panel">{loadError}</div>
  {:else if isLoading}
    <div class="status-panel">Loading usage...</div>
  {:else}
  <section class="storage-section">
    <div class="storage-header">
      <div class="storage-info">
        <h3>Storage Used</h3>
        <span class="storage-numbers">
          <span class="used">{formatBytes(usage.storageUsed)}</span>
          <span class="total">/ {formatBytes(usage.storageLimit)}</span>
        </span>
      </div>
      <div class="storage-percent">{storagePercentage.toFixed(1)}%</div>
    </div>
    
    <div class="progress-bar">
      <div class="progress-fill" style="width: {storagePercentage}%"></div>
    </div>
    <p class="storage-hint">Local testing uses filesystem storage under the backend data folder.</p>
  </section>

  <section class="stats-grid">
    <StatCard label="Total Shares (All Time)" value={usage.totalShares.toString()} />
    <StatCard label="Active Public Links" value={usage.activeLinks.toString()} accent />
    <StatCard label="Views Today" value={usage.viewsToday.toString()} />
  </section>
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
    display: flex;
    flex-direction: column;
    gap: var(--space-8);
  }

  .storage-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
  }

  .storage-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: var(--space-4);
  }

  .storage-info h3 {
    font-size: var(--text-sm);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-1);
  }

  .storage-numbers {
    display: flex;
    align-items: baseline;
    gap: var(--space-2);
  }

  .storage-numbers .used {
    font-size: var(--text-3xl);
    font-weight: var(--weight-bold);
    color: var(--text);
    letter-spacing: -0.02em;
  }

  .storage-numbers .total {
    font-size: var(--text-md);
    color: var(--text-secondary);
  }

  .storage-percent {
    font-size: var(--text-lg);
    font-weight: var(--weight-semibold);
    color: var(--accent);
  }

  .progress-bar {
    height: 8px;
    background: var(--elevated);
    border-radius: var(--radius-full);
    overflow: hidden;
    margin-bottom: var(--space-3);
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--snaply-cyan), var(--snaply-yellow));
    border-radius: var(--radius-full);
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .storage-hint {
    font-size: var(--text-sm);
    color: var(--text-muted);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--space-4);
  }

  .status-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    color: var(--text-secondary);
    padding: var(--space-6);
  }
</style>
