<script lang="ts">
  type Props = {
    title: string;
    description: string;
    actionLabel?: string;
    onaction?: () => void;
  };
  let { title, description, actionLabel = '', onaction }: Props = $props();
</script>

<div class="empty-state">
  <div class="empty-icon">
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
      <rect x="4" y="6" width="32" height="28" rx="4" stroke="currentColor" stroke-width="1.5" />
      <path d="M4 14h32" stroke="currentColor" stroke-width="1.5" />
      <circle cx="9" cy="10" r="1.5" fill="currentColor" />
      <circle cx="14" cy="10" r="1.5" fill="currentColor" />
      <circle cx="19" cy="10" r="1.5" fill="currentColor" />
    </svg>
  </div>
  <h3 class="empty-title">{title}</h3>
  <p class="empty-description">{description}</p>
  {#if actionLabel && onaction}
    <button class="empty-action" onclick={onaction}>
      {actionLabel}
    </button>
  {/if}
</div>

<style>
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: var(--space-12) var(--space-6);
    gap: var(--space-3);
  }

  .empty-icon {
    color: var(--text-muted);
    opacity: 0.4;
    margin-bottom: var(--space-2);
  }

  .empty-title {
    font-size: var(--text-md);
    font-weight: var(--weight-medium);
    color: var(--text-secondary);
  }

  .empty-description {
    font-size: var(--text-sm);
    color: var(--text-muted);
    max-width: 280px;
    line-height: var(--leading-relaxed);
  }

  .empty-action {
    margin-top: var(--space-3);
    padding: var(--space-2) var(--space-5);
    border-radius: var(--radius-md);
    background: var(--accent);
    color: white;
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    transition:
      background var(--transition-fast),
      transform var(--transition-fast);
  }

  .empty-action:hover {
    background: var(--accent-hover);
    transform: translateY(-1px);
  }

  .empty-action:active {
    transform: translateY(0);
  }
</style>
