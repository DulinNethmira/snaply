<script lang="ts">
  import type { Snippet } from 'svelte';

  type Props = {
    label: string;
    value: string;
    subtitle?: string;
    accent?: boolean;
    children?: Snippet;
  };
  let { label, value, subtitle = '', accent = false }: Props = $props();
</script>

<div class="stat-card" class:accent>
  <span class="stat-label">{label}</span>
  <span class="stat-value">{value}</span>
  {#if subtitle}
    <span class="stat-subtitle">{subtitle}</span>
  {/if}
</div>

<style>
  .stat-card {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    background: var(--surface);
    border: 1px solid var(--border);
    min-width: 0;
    transition: border-color var(--transition-fast);
  }

  .stat-card:hover {
    border-color: var(--border-hover);
  }

  .stat-card.accent {
    border-color: rgba(124, 109, 247, 0.15);
  }

  .stat-label {
    font-size: var(--text-xs);
    color: var(--text-muted);
    font-weight: var(--weight-medium);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }

  .stat-value {
    font-size: var(--text-xl);
    font-weight: var(--weight-semibold);
    color: var(--text);
    letter-spacing: -0.02em;
  }

  .stat-card.accent .stat-value {
    color: var(--accent);
  }

  .stat-subtitle {
    font-size: var(--text-xs);
    color: var(--text-muted);
  }
</style>
