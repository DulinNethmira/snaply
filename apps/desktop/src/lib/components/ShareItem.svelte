<script lang="ts">
  import type { ShareItem } from '$lib/types';
  import { formatBytes, formatRelativeTime, formatExpiry, getFileIcon } from '$lib/data/mock';
  import Copy from '$lib/icons/Copy.svelte';
  import ExternalLink from '$lib/icons/ExternalLink.svelte';
  import Trash from '$lib/icons/Trash.svelte';
  import File from '$lib/icons/File.svelte';
  import ImageIcon from '$lib/icons/Image.svelte';
  import Clipboard from '$lib/icons/Clipboard.svelte';

  type Props = { item: ShareItem };
  let { item }: Props = $props();

  let copied = $state(false);

  function copyLink() {
    navigator.clipboard.writeText(item.url);
    copied = true;
    setTimeout(() => { copied = false; }, 1500);
  }

  const iconMap = { file: File, image: ImageIcon, screenshot: ImageIcon, clipboard: Clipboard } as const;
  const IconComponent = $derived(iconMap[item.type]);
</script>

<div class="share-item" class:expired={item.status === 'expired'} data-id="share-{item.id}">
  <div class="item-icon" class:is-image={item.type === 'image' || item.type === 'screenshot'}>
    <IconComponent size={16} />
  </div>

  <div class="item-info">
    <span class="item-name truncate">{item.filename}</span>
    <span class="item-meta">
      {formatBytes(item.size)} · {formatRelativeTime(item.createdAt)}
    </span>
  </div>

  <div class="item-expiry" class:expired={item.status === 'expired'}>
    {formatExpiry(item.expiresAt)}
  </div>

  <div class="item-views">
    {item.views} views
  </div>

  <div class="item-actions">
    <button
      class="icon-btn"
      class:copied
      onclick={copyLink}
      title={copied ? 'Copied!' : 'Copy link'}
      aria-label="Copy link"
    >
      <Copy size={14} />
    </button>
    <button class="icon-btn" title="Open" aria-label="Open in browser">
      <ExternalLink size={14} />
    </button>
    <button class="icon-btn delete" title="Delete" aria-label="Delete share">
      <Trash size={14} />
    </button>
  </div>
</div>

<style>
  .share-item {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    transition: background var(--transition-fast);
  }

  .share-item:hover {
    background: var(--elevated);
  }

  .share-item.expired {
    opacity: 0.5;
  }

  .item-icon {
    width: 32px;
    height: 32px;
    border-radius: var(--radius-md);
    background: var(--elevated);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .item-icon.is-image {
    color: var(--accent);
    background: var(--accent-subtle);
  }

  .item-info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .item-name {
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
    color: var(--text);
  }

  .item-meta {
    font-size: var(--text-xs);
    color: var(--text-muted);
  }

  .item-expiry {
    font-size: var(--text-xs);
    color: var(--text-secondary);
    white-space: nowrap;
    padding: 2px var(--space-2);
    border-radius: var(--radius-full);
    background: var(--elevated);
  }

  .item-expiry.expired {
    color: var(--error);
    background: var(--error-subtle);
  }

  .item-views {
    font-size: var(--text-xs);
    color: var(--text-muted);
    white-space: nowrap;
    min-width: 55px;
    text-align: right;
  }

  .item-actions {
    display: flex;
    gap: var(--space-1);
    opacity: 0;
    transition: opacity var(--transition-fast);
  }

  .share-item:hover .item-actions {
    opacity: 1;
  }

  .icon-btn {
    width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    transition:
      color var(--transition-fast),
      background var(--transition-fast);
  }

  .icon-btn:hover {
    color: var(--text);
    background: var(--elevated-hover);
  }

  .icon-btn.copied {
    color: var(--success);
  }

  .icon-btn.delete:hover {
    color: var(--error);
  }
</style>
