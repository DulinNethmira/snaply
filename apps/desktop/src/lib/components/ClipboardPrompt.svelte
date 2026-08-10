<script lang="ts">
  import { clipboardState } from '$lib/stores/clipboard.svelte';
  import { addMemoryUpload } from '$lib/stores/upload.svelte';
  import { invoke } from '@tauri-apps/api/core';

  async function confirmShare() {
    const type = clipboardState.detectedType;
    clipboardState.showPrompt = false;

    if (type === 'image') {
        await addMemoryUpload('clipboard_image', `clipboard_${Date.now()}.png`, 'image/png');
    } else if (type === 'text' || type === 'url') {
        await addMemoryUpload('clipboard_text', `clipboard_${Date.now()}.txt`, 'text/plain', true);
    }
  }

  function cancelShare() {
    clipboardState.showPrompt = false;
  }
</script>

{#if clipboardState.showPrompt}
  <div class="clipboard-prompt-backdrop">
    <div class="clipboard-prompt-modal">
      <div class="modal-icon">
        {#if clipboardState.detectedType === 'image'}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
        {:else if clipboardState.detectedType === 'url'}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
        {:else}
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        {/if}
      </div>
      <h3>{clipboardState.detectedType === 'image' ? 'Image' : clipboardState.detectedType === 'url' ? 'Link' : 'Text'} detected</h3>
      <p>Would you like to share the contents of your clipboard?</p>
      
      <div class="modal-actions">
        <button class="btn-secondary" onclick={cancelShare}>Cancel</button>
        <button class="btn-primary" onclick={confirmShare}>Share</button>
      </div>
    </div>
  </div>
{/if}

<style>
  .clipboard-prompt-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
  }

  .clipboard-prompt-modal {
    background-color: var(--surface-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: var(--space-6);
    width: 100%;
    max-width: 400px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    text-align: center;
    animation: scaleIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  }

  @keyframes scaleIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  .modal-icon {
    width: 48px;
    height: 48px;
    background-color: var(--surface-secondary);
    border-radius: var(--radius-full);
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto var(--space-4);
    color: var(--accent-primary);
  }

  h3 {
    margin: 0 0 var(--space-2);
    font-size: var(--font-lg);
    color: var(--text-primary);
  }

  p {
    margin: 0 0 var(--space-6);
    color: var(--text-secondary);
    font-size: var(--font-sm);
  }

  .modal-actions {
    display: flex;
    gap: var(--space-3);
    justify-content: center;
  }

  .btn-primary, .btn-secondary {
    padding: var(--space-2) var(--space-6);
    border-radius: var(--radius-md);
    font-size: var(--font-sm);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-primary {
    background-color: var(--accent-primary);
    color: white;
    border: none;
  }

  .btn-primary:hover {
    background-color: var(--accent-hover);
  }

  .btn-secondary {
    background-color: transparent;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
  }

  .btn-secondary:hover {
    background-color: var(--surface-secondary);
  }
</style>
