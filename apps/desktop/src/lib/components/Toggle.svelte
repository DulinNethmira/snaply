<script lang="ts">
  type Props = {
    label: string;
    checked: boolean;
    onchange?: (value: boolean) => void;
  };
  let { label, checked = $bindable(), onchange }: Props = $props();

  function toggle() {
    checked = !checked;
    onchange?.(checked);
  }
</script>

<button class="toggle-row" onclick={toggle} role="switch" aria-checked={checked}>
  <span class="toggle-label">{label}</span>
  <div class="toggle-track" class:active={checked}>
    <div class="toggle-thumb"></div>
  </div>
</button>

<style>
  .toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-3) var(--space-4);
    border-radius: var(--radius-md);
    width: 100%;
    transition: background var(--transition-fast);
  }

  .toggle-row:hover {
    background: var(--elevated);
  }

  .toggle-label {
    font-size: var(--text-sm);
    color: var(--text);
  }

  .toggle-track {
    width: 36px;
    height: 20px;
    border-radius: var(--radius-full);
    background: var(--elevated-hover);
    position: relative;
    transition: background var(--transition-normal);
    flex-shrink: 0;
  }

  .toggle-track.active {
    background: var(--accent);
  }

  .toggle-thumb {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: white;
    position: absolute;
    top: 3px;
    left: 3px;
    transition: transform var(--transition-normal);
  }

  .toggle-track.active .toggle-thumb {
    transform: translateX(16px);
  }
</style>
