<script lang="ts">
  import type { UploadState } from '$lib/types';
  import Upload from '$lib/icons/Upload.svelte';
  import Camera from '$lib/icons/Camera.svelte';
  import Clipboard from '$lib/icons/Clipboard.svelte';
  import Check from '$lib/icons/Check.svelte';

  let uploadState: UploadState = $state('idle');
  let progress = $state(0);
  let dragCounter = $state(0);

  function handleDragEnter(e: DragEvent) {
    e.preventDefault();
    dragCounter++;
    if (uploadState === 'idle' || uploadState === 'hover') {
      uploadState = 'dragging';
    }
  }

  function handleDragLeave(e: DragEvent) {
    e.preventDefault();
    dragCounter--;
    if (dragCounter <= 0) {
      dragCounter = 0;
      if (uploadState === 'dragging') uploadState = 'idle';
    }
  }

  function handleDragOver(e: DragEvent) {
    e.preventDefault();
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragCounter = 0;
    simulateUpload();
  }

  function simulateUpload() {
    uploadState = 'uploading';
    progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15 + 5;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        uploadState = 'processing';
        setTimeout(() => {
          uploadState = 'success';
          setTimeout(() => {
            uploadState = 'idle';
          }, 2000);
        }, 800);
      }
    }, 150);
  }

  function handleMouseEnter() {
    if (uploadState === 'idle') uploadState = 'hover';
  }

  function handleMouseLeave() {
    if (uploadState === 'hover') uploadState = 'idle';
  }
</script>

<div
  class="dropzone"
  class:hover={uploadState === 'hover'}
  class:dragging={uploadState === 'dragging'}
  class:uploading={uploadState === 'uploading'}
  class:processing={uploadState === 'processing'}
  class:success={uploadState === 'success'}
  role="button"
  tabindex="0"
  aria-label="Drop files to upload"
  ondragenter={handleDragEnter}
  ondragleave={handleDragLeave}
  ondragover={handleDragOver}
  ondrop={handleDrop}
  onmouseenter={handleMouseEnter}
  onmouseleave={handleMouseLeave}
>
  <div class="dropzone-border"></div>

  <div class="dropzone-content">
    {#if uploadState === 'success'}
      <div class="state-icon success-icon">
        <Check size={24} />
      </div>
      <p class="dropzone-title">Shared successfully</p>
      <p class="dropzone-subtitle">Link copied to clipboard</p>
    {:else if uploadState === 'uploading' || uploadState === 'processing'}
      <div class="progress-ring">
        <svg viewBox="0 0 48 48">
          <circle class="progress-bg" cx="24" cy="24" r="20" />
          <circle
            class="progress-fill"
            cx="24"
            cy="24"
            r="20"
            style="stroke-dashoffset: {125.6 - (125.6 * progress) / 100}"
          />
        </svg>
        <span class="progress-text">{Math.round(progress)}%</span>
      </div>
      <p class="dropzone-title">
        {uploadState === 'processing' ? 'Processing...' : 'Uploading...'}
      </p>
    {:else}
      <div class="state-icon upload-icon">
        <Upload size={22} />
      </div>
      <p class="dropzone-title">Drop anything here</p>
      <p class="dropzone-subtitle">Files, screenshots, images and more</p>
    {/if}
  </div>

  {#if uploadState === 'idle' || uploadState === 'hover'}
    <div class="dropzone-actions">
      <button class="action-btn" onclick={() => simulateUpload()} data-id="btn-capture">
        <Camera size={15} />
        <span>Capture Screenshot</span>
      </button>
      <button class="action-btn" onclick={() => simulateUpload()} data-id="btn-upload">
        <Upload size={15} />
        <span>Upload File</span>
      </button>
      <button class="action-btn" onclick={() => simulateUpload()} data-id="btn-clipboard">
        <Clipboard size={15} />
        <span>Share Clipboard</span>
      </button>
    </div>
  {/if}
</div>

<style>
  .dropzone {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: var(--space-5);
    padding: var(--space-8) var(--space-6);
    border-radius: var(--radius-xl);
    background: var(--surface);
    transition: background var(--transition-normal);
    overflow: hidden;
    min-height: 200px;
  }

  .dropzone-border {
    position: absolute;
    inset: 0;
    border-radius: var(--radius-xl);
    border: 1.5px dashed var(--border-hover);
    pointer-events: none;
    transition:
      border-color var(--transition-normal),
      opacity var(--transition-normal);
  }

  .dropzone.hover .dropzone-border,
  .dropzone.dragging .dropzone-border {
    border-color: var(--accent);
    opacity: 1;
  }

  .dropzone.dragging {
    background: var(--accent-subtle);
  }

  .dropzone.uploading .dropzone-border,
  .dropzone.processing .dropzone-border,
  .dropzone.success .dropzone-border {
    border-style: solid;
    border-color: var(--border);
  }

  .dropzone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--space-2);
    z-index: 1;
  }

  .state-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--space-2);
    transition: transform var(--transition-normal);
  }

  .upload-icon {
    background: var(--accent-subtle);
    color: var(--accent);
  }

  .success-icon {
    background: var(--success-subtle);
    color: var(--success);
    animation: scaleIn 280ms ease;
  }

  .dropzone.hover .upload-icon {
    transform: translateY(-2px);
  }

  .dropzone-title {
    font-size: var(--text-md);
    font-weight: var(--weight-medium);
    color: var(--text);
  }

  .dropzone-subtitle {
    font-size: var(--text-sm);
    color: var(--text-muted);
  }

  /* ── Progress ── */
  .progress-ring {
    position: relative;
    width: 48px;
    height: 48px;
    margin-bottom: var(--space-2);
  }

  .progress-ring svg {
    transform: rotate(-90deg);
    width: 100%;
    height: 100%;
  }

  .progress-bg {
    fill: none;
    stroke: var(--border);
    stroke-width: 3;
  }

  .progress-fill {
    fill: none;
    stroke: var(--accent);
    stroke-width: 3;
    stroke-linecap: round;
    stroke-dasharray: 125.6;
    transition: stroke-dashoffset var(--transition-fast);
  }

  .progress-text {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: var(--text-xs);
    font-weight: var(--weight-semibold);
    color: var(--text-secondary);
  }

  /* ── Actions ── */
  .dropzone-actions {
    display: flex;
    gap: var(--space-2);
    z-index: 1;
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-3);
    border-radius: var(--radius-md);
    background: var(--elevated);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    font-size: var(--text-xs);
    font-weight: var(--weight-medium);
    transition:
      color var(--transition-fast),
      background var(--transition-fast),
      border-color var(--transition-fast);
  }

  .action-btn:hover {
    color: var(--text);
    background: var(--elevated-hover);
    border-color: var(--border-hover);
  }

  @keyframes scaleIn {
    from { transform: scale(0.8); opacity: 0; }
    to { transform: scale(1); opacity: 1; }
  }
</style>
