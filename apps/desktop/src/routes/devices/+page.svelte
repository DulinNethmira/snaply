<script lang="ts">
  import EmptyState from '$lib/components/EmptyState.svelte';
  import Monitor from '$lib/icons/Monitor.svelte';
  import { onMount } from 'svelte';

  let platform = $state('Windows');
  let deviceName = $state('This device');

  onMount(() => {
    const browserNavigator = navigator as Navigator & { userAgentData?: { platform?: string } };
    platform = browserNavigator.userAgentData?.platform || navigator.platform || 'Windows';
    deviceName = platform.includes('Win') ? 'Windows PC' : 'This device';
  });
</script>

<div class="page-header">
  <h1 class="page-title">Devices</h1>
  <p class="page-subtitle">Devices connected to your Snaply account.</p>
</div>

<div class="page-content">
  <div class="device-list">
    <div class="device-item">
      <div class="device-icon online">
        <Monitor size={20} />
      </div>
      <div class="device-info">
        <div class="device-name">{deviceName}</div>
        <div class="device-meta">
          {platform} · <span class="status-online">Current local session</span>
        </div>
      </div>
    </div>
  </div>

  <div class="connect-more">
    <EmptyState
      title="Multi-device sync is not active yet"
      description="Local testing only shows this computer. Real device sync needs the hosted backend and device registration API."
    />
  </div>
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
    gap: var(--space-6);
  }

  .device-list {
    display: flex;
    flex-direction: column;
    gap: var(--space-2);
  }

  .device-item {
    display: flex;
    align-items: center;
    gap: var(--space-4);
    padding: var(--space-4);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    transition: border-color var(--transition-fast);
  }

  .device-item:hover {
    border-color: var(--border-hover);
  }

  .device-icon {
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    background: var(--elevated);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    position: relative;
  }

  .device-icon.online {
    color: var(--accent);
    background: var(--accent-subtle);
  }

  .device-icon.online::after {
    content: '';
    position: absolute;
    bottom: -2px;
    right: -2px;
    width: 10px;
    height: 10px;
    background: var(--success);
    border: 2px solid var(--surface);
    border-radius: 50%;
  }

  .device-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .device-name {
    font-size: var(--text-md);
    font-weight: var(--weight-medium);
    color: var(--text);
  }

  .device-meta {
    font-size: var(--text-sm);
    color: var(--text-muted);
  }

  .status-online {
    color: var(--success);
  }

  .connect-more {
    border: 1px dashed var(--border);
    border-radius: var(--radius-xl);
  }
</style>
