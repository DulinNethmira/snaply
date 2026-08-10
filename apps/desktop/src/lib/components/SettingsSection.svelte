<script lang="ts">
  import type { Snippet } from 'svelte';

  type Props = {
    title: string;
    children: Snippet;
  };
  let { title, children }: Props = $props();
</script>

<section class="settings-section">
  <h3 class="section-title">{title}</h3>
  <div class="section-content">
    {@render children()}
  </div>
</section>

<style>
  .settings-section {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
  }

  .section-title {
    font-size: var(--text-sm);
    font-weight: var(--weight-semibold);
    color: var(--text);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding-bottom: var(--space-2);
    border-bottom: 1px solid var(--border);
  }

  .section-content {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }
</style>
