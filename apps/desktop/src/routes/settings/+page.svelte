<script lang="ts">
  import SettingsSection from '$lib/components/SettingsSection.svelte';
  import Toggle from '$lib/components/Toggle.svelte';
  import { mockSettings } from '$lib/data/mock';

  let settings = $state(mockSettings);
</script>

<div class="page-header">
  <h1 class="page-title">Settings</h1>
  <p class="page-subtitle">Configure Snaply to work exactly how you want.</p>
</div>

<div class="page-content">
  <div class="settings-layout">
    <!-- Left Column -->
    <div class="settings-column">
      <SettingsSection title="General">
        <Toggle label="Launch at startup" bind:checked={settings.general.launchAtStartup} />
        <Toggle label="Minimize to system tray" bind:checked={settings.general.minimizeToTray} />
        <Toggle label="Enable notifications" bind:checked={settings.general.notifications} />
      </SettingsSection>

      <SettingsSection title="Shortcuts">
        <div class="shortcut-row">
          <span class="shortcut-label">Capture Screenshot</span>
          <kbd class="shortcut-key">{settings.shortcuts.captureScreen}</kbd>
        </div>
        <div class="shortcut-row">
          <span class="shortcut-label">Capture Area</span>
          <kbd class="shortcut-key">{settings.shortcuts.captureArea}</kbd>
        </div>
        <div class="shortcut-row">
          <span class="shortcut-label">Upload Clipboard</span>
          <kbd class="shortcut-key">{settings.shortcuts.uploadClipboard}</kbd>
        </div>
      </SettingsSection>

      <SettingsSection title="Appearance">
        <div class="setting-row">
          <label for="theme-select">Theme</label>
          <select id="theme-select" bind:value={settings.appearance.theme}>
            <option value="dark">Dark (Default)</option>
            <option value="light">Light</option>
            <option value="system">System match</option>
          </select>
        </div>
        <Toggle label="Compact mode" bind:checked={settings.appearance.compactMode} />
      </SettingsSection>
    </div>

    <!-- Right Column -->
    <div class="settings-column">
      <SettingsSection title="Uploads">
        <Toggle label="Auto-upload screenshots" bind:checked={settings.uploads.autoUpload} />
        
        <div class="setting-row">
          <label for="expiry-select">Default link expiry</label>
          <select id="expiry-select" bind:value={settings.uploads.defaultExpiry}>
            <option value="1h">1 Hour</option>
            <option value="24h">24 Hours</option>
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
            <option value="never">Never expire</option>
          </select>
        </div>

        <div class="setting-row">
          <label for="quality-select">Image quality</label>
          <select id="quality-select" bind:value={settings.uploads.quality}>
            <option value="original">Original (Lossless)</option>
            <option value="high">High (Optimized)</option>
            <option value="medium">Medium (Fastest upload)</option>
          </select>
        </div>
      </SettingsSection>

      <SettingsSection title="Privacy">
        <Toggle label="Strip EXIF metadata from images" bind:checked={settings.privacy.stripMetadata} />
        <Toggle label="Require password for links" bind:checked={settings.privacy.requirePassword} />
      </SettingsSection>

      <SettingsSection title="Account">
        <div class="about-info">
          <button class="btn-secondary" style="width: 100%; border-color: #ef4444; color: #ef4444;" onclick={async () => {
              import('$lib/api').then(api => {
                  api.logout().then(() => {
                      window.location.reload();
                  });
              });
          }}>Logout</button>
        </div>
      </SettingsSection>

      <SettingsSection title="About">
        <div class="about-info">
          <div class="app-version">
            {#await import('@tauri-apps/api/app').then(m => m.getVersion())}
              Loading version...
            {:then v}
              Snaply v{v}
            {/await}
          </div>
          <div class="app-links">
            <button 
              class="btn-link"
              style="padding: 0; text-align: left;"
              onclick={async () => {
                const { invoke } = await import('@tauri-apps/api/core');
                try {
                  const hasUpdate = await invoke('check_update');
                  if (!hasUpdate) {
                    alert('You are on the latest version!');
                  }
                } catch (e) {
                  alert('Update check failed: ' + e);
                }
              }}
            >Check for updates</button>
            <a href="https://snaply-dev.github.io/terms" target="_blank">Terms of Service</a>
            <a href="https://snaply-dev.github.io/privacy" target="_blank">Privacy Policy</a>
          </div>
        </div>
      </SettingsSection>
    </div>
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
    max-width: 900px;
  }

  .settings-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--space-8);
  }

  .settings-column {
    display: flex;
    flex-direction: column;
    gap: var(--space-8);
  }

  .shortcut-row,
  .setting-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
  }

  .shortcut-row {
    background: var(--surface);
    border: 1px solid var(--border);
  }

  .shortcut-label,
  .setting-row label {
    font-size: var(--text-sm);
    color: var(--text);
  }

  .shortcut-key {
    font-family: var(--font-mono);
    font-size: var(--text-xs);
    background: var(--elevated);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid var(--border-hover);
    color: var(--text-secondary);
  }

  select {
    background: var(--elevated);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 4px 8px;
    border-radius: var(--radius-sm);
    font-size: var(--text-sm);
    cursor: pointer;
  }

  select:focus {
    border-color: var(--accent);
  }

  .about-info {
    padding: var(--space-2) var(--space-4);
  }

  .app-version {
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    color: var(--text);
    margin-bottom: var(--space-2);
  }

  .app-links {
    display: flex;
    flex-direction: column;
    gap: var(--space-1);
  }

  .app-links a, .app-links button {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    background: none;
    border: none;
    cursor: pointer;
    text-decoration: none;
  }

  .app-links a:hover, .app-links button:hover {
    color: var(--accent);
  }

  @media (max-width: 768px) {
    .settings-layout {
      grid-template-columns: 1fr;
    }
  }
</style>
