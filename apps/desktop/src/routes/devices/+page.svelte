<script lang="ts">
  import EmptyState from '$lib/components/EmptyState.svelte';
  import { mockDevices, formatRelativeTime } from '$lib/data/mock';
  import Monitor from '$lib/icons/Monitor.svelte';

</script>

<div class="page-header">
  <h1 class="page-title">Devices</h1>
  <p class="page-subtitle">Computers and phones connected to your Snaply account.</p>
</div>

<div class="page-content">
  <div class="device-list">
    {#each mockDevices as device (device.id)}
      <div class="device-item">
        <div class="device-icon" class:online={device.isOnline}>
          <Monitor size={20} />
        </div>
        <div class="device-info">
          <div class="device-name">{device.name}</div>
          <div class="device-meta">
            {device.os} · 
            {#if device.isOnline}
              <span class="status-online">Online now</span>
            {:else}
              Last seen {formatRelativeTime(device.lastSeen)}
            {/if}
          </div>
        </div>
        <div class="device-actions">
          <button class="remove-btn">Remove</button>
        </div>
      </div>
    {/each}
  </div>

  <div class="connect-more">
    <EmptyState
      title="Connect another device"
      description="Download Snaply on your phone or tablet to easily share clipboards and files between devices."
      actionLabel="Get Download Link"
      onaction={() => console.log('Get download link')}
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

  .remove-btn {
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    color: var(--text-secondary);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    background: var(--elevated);
    transition: background var(--transition-fast), color var(--transition-fast);
  }

  .remove-btn:hover {
    background: var(--error-subtle);
    color: var(--error);
  }

  .connect-more {
    border: 1px dashed var(--border);
    border-radius: var(--radius-xl);
  }
</style>
