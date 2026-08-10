<script lang="ts">
  import { page } from '$app/stores';
  import Home from '$lib/icons/Home.svelte';
  import Clock from '$lib/icons/Clock.svelte';
  import Monitor from '$lib/icons/Monitor.svelte';
  import BarChart from '$lib/icons/BarChart.svelte';
  import Settings from '$lib/icons/Settings.svelte';

  const navItems = [
    { id: 'overview', label: 'Overview', path: '/', icon: Home },
    { id: 'recent', label: 'Recent', path: '/recent', icon: Clock },
    { id: 'devices', label: 'Devices', path: '/devices', icon: Monitor },
    { id: 'usage', label: 'Usage', path: '/usage', icon: BarChart },
    { id: 'settings', label: 'Settings', path: '/settings', icon: Settings }
  ] as const;

  function isActive(currentPath: string, itemPath: string): boolean {
    if (itemPath === '/') return currentPath === '/';
    return currentPath.startsWith(itemPath);
  }
</script>

<nav class="sidebar" aria-label="Main navigation">
  <div class="sidebar-brand">
    <div class="brand-icon">S</div>
    <span class="brand-name">Snaply</span>
  </div>

  <ul class="nav-list">
    {#each navItems as item}
      {@const active = isActive($page.url.pathname, item.path)}
      <li>
        <a
          href={item.path}
          class="nav-item"
          class:active
          aria-current={active ? 'page' : undefined}
          data-id="nav-{item.id}"
        >
          <span class="nav-indicator"></span>
          <item.icon size={18} />
          <span class="nav-label">{item.label}</span>
        </a>
      </li>
    {/each}
  </ul>

  <div class="sidebar-footer">
    <div class="connection-dot"></div>
    <span class="connection-text">Connected</span>
  </div>
</nav>

<style>
  .sidebar {
    display: flex;
    flex-direction: column;
    width: var(--sidebar-width);
    min-width: var(--sidebar-width);
    height: 100vh;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: var(--space-4) 0;
    overflow-y: auto;
  }

  .sidebar-brand {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-5);
    margin-bottom: var(--space-6);
  }

  .brand-icon {
    width: 28px;
    height: 28px;
    border-radius: var(--radius-lg);
    background: linear-gradient(135deg, var(--accent), #9B8AFB);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: var(--weight-bold);
    font-size: var(--text-sm);
    color: white;
    flex-shrink: 0;
  }

  .brand-name {
    font-size: var(--text-md);
    font-weight: var(--weight-semibold);
    color: var(--text);
    letter-spacing: -0.01em;
  }

  .nav-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
    padding: 0 var(--space-2);
    flex: 1;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    text-decoration: none;
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    position: relative;
    transition:
      color var(--transition-fast),
      background var(--transition-fast);
  }

  .nav-item:hover {
    color: var(--text);
    background: var(--elevated);
  }

  .nav-item.active {
    color: var(--text);
    background: var(--elevated);
  }

  .nav-indicator {
    position: absolute;
    left: -8px;
    top: 50%;
    transform: translateY(-50%) scaleY(0);
    width: 3px;
    height: 16px;
    background: var(--accent);
    border-radius: var(--radius-full);
    transition: transform var(--transition-normal);
  }

  .nav-item.active .nav-indicator {
    transform: translateY(-50%) scaleY(1);
  }

  .nav-label {
    white-space: nowrap;
  }

  .sidebar-footer {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-3) var(--space-5);
    border-top: 1px solid var(--border);
    margin-top: var(--space-2);
  }

  .connection-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--success);
    box-shadow: 0 0 6px var(--success);
    flex-shrink: 0;
  }

  .connection-text {
    font-size: var(--text-xs);
    color: var(--text-muted);
  }
</style>
