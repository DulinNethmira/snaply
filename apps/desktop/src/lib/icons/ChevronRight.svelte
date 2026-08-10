<script lang="ts">
  type Props = { size?: number; class?: string };
  let { size = 18, class: className = '' }: Props = $props();
</script>

<svg
  xmlns="http://www.w3.org/2000/svg"
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width="1.75"
  stroke-linecap="round"
  stroke-linejoin="round"
  class={className}
>
  <polyline points="9 18 15 12 9 6" />
</svg>
