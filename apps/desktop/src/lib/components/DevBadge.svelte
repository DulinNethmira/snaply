<!--
  DevBadge — shows a subtle "LOCAL" pill in the UI when running in dev mode.
  Only rendered in development builds (import.meta.env.DEV === true).
  In production builds Vite tree-shakes this entire component away.
-->
<script lang="ts">
  const isDev = import.meta.env.DEV;
</script>

{#if isDev}
  <div class="dev-badge" title="Running in local development mode">
    <span class="dev-dot"></span>
    LOCAL
  </div>
{/if}

<style>
  .dev-badge {
    position: fixed;
    bottom: 12px;
    right: 14px;
    z-index: 9999;
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 3px 9px;
    border-radius: 99px;
    background: var(--snaply-yellow-muted);
    border: 1px solid rgba(255, 193, 49, 0.35);
    color: var(--snaply-yellow);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    pointer-events: none;
    user-select: none;
    backdrop-filter: blur(4px);
    font-family: 'SF Mono', 'Fira Mono', monospace;
  }

  .dev-dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--snaply-yellow);
    animation: pulse 2s ease-in-out infinite;
    flex-shrink: 0;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
</style>
