<script lang="ts">
  import { uploadState, cancelUpload } from '$lib/stores/upload.svelte';

  const activeUploads = $derived(uploadState.queue.filter(t => t.state === 'Uploading' || t.state === 'Queued'));

  function formatBytes(bytes: number) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function formatTime(seconds: number) {
    if (!seconds || !isFinite(seconds)) return '--';
    if (seconds < 60) return Math.ceil(seconds) + 's';
    return Math.ceil(seconds / 60) + 'm ' + Math.ceil(seconds % 60) + 's';
  }
</script>

{#if activeUploads.length > 0}
  <div class="upload-queue">
    <div class="queue-header">
      <h4>Active Uploads ({activeUploads.length})</h4>
    </div>
    <div class="queue-list">
      {#each activeUploads as task}
        <div class="upload-item">
          <div class="item-info">
            <span class="filename" title={task.filename}>{task.filename}</span>
            <span class="status">{task.state}</span>
          </div>
          <div class="progress-container">
            <div 
              class="progress-bar" 
              style="width: {task.totalBytes > 0 ? (task.uploadedBytes / task.totalBytes) * 100 : 0}%"
            ></div>
          </div>
          <div class="item-stats">
            <span>{formatBytes(task.uploadedBytes)} / {formatBytes(task.totalBytes)}</span>
            <span>{formatBytes(task.speedBps)}/s</span>
            <span>ETA: {formatTime(task.etaSeconds)}</span>
          </div>
          <div class="item-actions">
            <button onclick={() => cancelUpload(task.id)} class="btn-cancel">Cancel</button>
          </div>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  .upload-queue {
    position: fixed;
    bottom: var(--space-6);
    right: var(--space-6);
    width: 350px;
    background-color: var(--surface-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    z-index: 1000;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .queue-header {
    padding: var(--space-3) var(--space-4);
    background-color: var(--surface-tertiary);
    border-bottom: 1px solid var(--border-color);
  }

  .queue-header h4 {
    margin: 0;
    font-size: var(--font-sm);
    color: var(--text-primary);
  }

  .queue-list {
    max-height: 400px;
    overflow-y: auto;
    padding: var(--space-3);
    display: flex;
    flex-direction: column;
    gap: var(--space-3);
  }

  .upload-item {
    background-color: var(--surface-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--space-3);
  }

  .item-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-2);
  }

  .filename {
    font-size: var(--font-sm);
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 70%;
  }

  .status {
    font-size: var(--font-xs);
    color: var(--accent-primary);
  }

  .progress-container {
    height: 6px;
    background-color: var(--surface-tertiary);
    border-radius: var(--radius-full);
    overflow: hidden;
    margin-bottom: var(--space-2);
  }

  .progress-bar {
    height: 100%;
    background-color: var(--accent-primary);
    border-radius: var(--radius-full);
    transition: width 0.2s linear;
  }

  .item-stats {
    display: flex;
    justify-content: space-between;
    font-size: var(--font-xs);
    color: var(--text-secondary);
    margin-bottom: var(--space-3);
  }

  .item-actions {
    display: flex;
    justify-content: flex-end;
  }

  .btn-cancel {
    background-color: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: var(--space-1) var(--space-3);
    border-radius: var(--radius-sm);
    font-size: var(--font-xs);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn-cancel:hover {
    background-color: rgba(255, 100, 100, 0.1);
    color: #ff6b6b;
    border-color: #ff6b6b;
  }
</style>
