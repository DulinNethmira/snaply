<script lang="ts">
  import DropZone from '$lib/components/DropZone.svelte';
  import StatCard from '$lib/components/StatCard.svelte';
  import ShareItemComponent from '$lib/components/ShareItem.svelte';
  import { formatBytes, formatRelativeTime, formatExpiry, getGreeting } from '$lib/data/mock';
  import ChevronRight from '$lib/icons/ChevronRight.svelte';
  import { onMount } from 'svelte';
  import { getRecentShares, getUsageStats } from '$lib/api';

  let recentShares: any[] = $state([]);
  let usage: any = $state({ totalShares: 0, storageUsed: 0, storageLimit: 5368709120, activeLinks: 0, sharesToday: 0, viewsToday: 0 });

  onMount(async () => {
      try {
          const shares = await getRecentShares();
          recentShares = shares.slice(0, 3);
          usage = await getUsageStats();
      } catch (e) {
          console.error(e);
      }
  });
</script>

<div class="page-header">
  <div>
    <h1 class="page-title">{getGreeting()}</h1>
    <p class="page-subtitle">Ready to share something new?</p>
  </div>
</div>

<div class="page-content">
  <section class="main-action">
    <DropZone />
  </section>

  <section class="quick-stats">
    <StatCard
      label="Shares Today"
      value={usage.sharesToday.toString()}
      accent={true}
    />
    <StatCard
      label="Storage Used"
      value={formatBytes(usage.storageUsed)}
      subtitle="{Math.round((usage.storageUsed / usage.storageLimit) * 100)}% of limit"
    />
    <StatCard
      label="Active Links"
      value={usage.activeLinks.toString()}
    />
  </section>

  <section class="recent-section">
    <div class="section-header">
      <h2>Recent Shares</h2>
      <a href="/recent" class="view-all">
        View all <ChevronRight size={14} />
      </a>
    </div>

    <div class="shares-list">
      {#each recentShares as item (item.id)}
        <ShareItemComponent {item} />
      {/each}
    </div>
  </section>
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
    display: flex;
    flex-direction: column;
    gap: var(--space-8);
    max-width: 800px;
  }

  .quick-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-4);
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--space-4);
  }

  .section-header h2 {
    font-size: var(--text-lg);
    font-weight: var(--weight-semibold);
  }

  .view-all {
    display: flex;
    align-items: center;
    gap: 2px;
    font-size: var(--text-sm);
    color: var(--text-secondary);
    font-weight: var(--weight-medium);
  }

  .view-all:hover {
    color: var(--accent);
  }

  .shares-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
</style>
