<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';

  let monitorName = '';
  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null;
  let imageBlobUrl: string | null = null;

  let isDragging = false;
  let startX = 0;
  let startY = 0;
  let currentX = 0;
  let currentY = 0;

  // For dimensions
  let rectWidth = 0;
  let rectHeight = 0;

  onMount(() => {
    // Get monitor name from URL search params
    const params = new URLSearchParams(window.location.search);
    monitorName = params.get('monitor') || '';

    if (canvas) {
      ctx = canvas.getContext('2d');
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }

    (async () => {
      try {
        // Fetch PNG bytes from Rust
        const bytes: Uint8Array = await invoke('get_monitor_capture', { monitorName });
        const blob = new Blob([bytes], { type: 'image/png' });
        imageBlobUrl = URL.createObjectURL(blob);
        
        const img = new Image();
        img.onload = () => {
          if (ctx) {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            drawOverlay();
          }
        };
        img.src = imageBlobUrl;
      } catch (e) {
        console.error('Failed to load capture:', e);
      }
    })();

    window.addEventListener('keydown', handleKeydown);
    return () => {
      if (imageBlobUrl) URL.revokeObjectURL(imageBlobUrl);
      window.removeEventListener('keydown', handleKeydown);
    };
  });

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      invoke('cancel_capture');
    }
  }

  function drawOverlay() {
    if (!ctx) return;
    
    // 1. Redraw base image
    if (imageBlobUrl) {
      const img = new Image();
      img.src = imageBlobUrl;
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    }

    // 2. Draw dark dimming overlay
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 3. Clear the dragged area if any
    if (rectWidth > 0 && rectHeight > 0) {
      const x = Math.min(startX, currentX);
      const y = Math.min(startY, currentY);
      ctx.clearRect(x, y, rectWidth, rectHeight);
      
      // Draw border
      ctx.strokeStyle = '#7C6DF7'; // Accent color
      ctx.lineWidth = 1.5;
      ctx.strokeRect(x, y, rectWidth, rectHeight);
    }
  }

  function onMouseDown(e: MouseEvent) {
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
    currentX = e.clientX;
    currentY = e.clientY;
    updateRect();
  }

  function onMouseMove(e: MouseEvent) {
    if (!isDragging) return;
    currentX = e.clientX;
    currentY = e.clientY;
    updateRect();
    drawOverlay();
  }

  function onMouseUp(e: MouseEvent) {
    if (!isDragging) return;
    isDragging = false;
    currentX = e.clientX;
    currentY = e.clientY;
    updateRect();
    
    if (rectWidth > 5 && rectHeight > 5) {
      const x = Math.min(startX, currentX);
      const y = Math.min(startY, currentY);
      
      // Send crop command to Rust
      invoke('crop_and_preview', {
        monitorName,
        x: Math.round(x),
        y: Math.round(y),
        width: Math.round(rectWidth),
        height: Math.round(rectHeight)
      }).catch(err => console.error(err));
    } else {
      // Too small, reset selection
      rectWidth = 0;
      rectHeight = 0;
      drawOverlay();
    }
  }

  function updateRect() {
    rectWidth = Math.abs(currentX - startX);
    rectHeight = Math.abs(currentY - startY);
  }
</script>

<div class="overlay-container">
  <canvas
    bind:this={canvas}
    onmousedown={onMouseDown}
    onmousemove={onMouseMove}
    onmouseup={onMouseUp}
  ></canvas>
  
  {#if isDragging && rectWidth > 5}
    <div 
      class="dimensions"
      style="left: {Math.max(currentX, startX) + 10}px; top: {Math.max(currentY, startY) + 10}px;"
    >
      {Math.round(rectWidth)} &times; {Math.round(rectHeight)}
    </div>
  {/if}
</div>

<style>
  :global(body) {
    background: transparent !important;
    overflow: hidden;
    margin: 0;
    padding: 0;
    cursor: crosshair;
  }
  
  .overlay-container {
    position: relative;
    width: 100vw;
    height: 100vh;
  }

  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }

  .dimensions {
    position: absolute;
    background: rgba(13, 17, 24, 0.85);
    color: white;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 8px;
    border-radius: 4px;
    pointer-events: none;
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    z-index: 10;
  }
</style>
