<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';

  let canvas: HTMLCanvasElement;
  let ctx: CanvasRenderingContext2D | null;
  let imageBlobUrl: string | null = null;
  let baseImage: HTMLImageElement | null = null;

  let currentTool: 'arrow' | 'rect' | 'circle' = 'rect';
  let isDrawing = false;
  let startX = 0;
  let startY = 0;
  
  // Store strokes to redraw
  type Stroke = { tool: string; x1: number; y1: number; x2: number; y2: number };
  let strokes: Stroke[] = [];

  onMount(() => {
    (async () => {
      try {
        const bytes: Uint8Array = await invoke('get_monitor_capture', { monitorName: 'preview' });
        const blob = new Blob([bytes], { type: 'image/png' });
        imageBlobUrl = URL.createObjectURL(blob);
        
        baseImage = new Image();
        baseImage.onload = () => {
          if (canvas) {
            canvas.width = baseImage!.width;
            canvas.height = baseImage!.height;
            ctx = canvas.getContext('2d');
            redraw();
          }
        };
        baseImage.src = imageBlobUrl;
      } catch (e) {
        console.error('Failed to load preview:', e);
      }
    })();

    return () => {
      if (imageBlobUrl) URL.revokeObjectURL(imageBlobUrl);
    };
  });

  function redraw() {
    if (!ctx || !baseImage) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(baseImage, 0, 0);
    
    ctx.strokeStyle = '#F87171'; // Red for annotations
    ctx.lineWidth = 3;
    
    for (const stroke of strokes) {
      drawShape(stroke.tool, stroke.x1, stroke.y1, stroke.x2, stroke.y2);
    }
  }

  function drawShape(tool: string, x1: number, y1: number, x2: number, y2: number) {
    if (!ctx) return;
    ctx.beginPath();
    if (tool === 'rect') {
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
    } else if (tool === 'circle') {
      const r = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
      ctx.arc(x1, y1, r, 0, 2 * Math.PI);
      ctx.stroke();
    } else if (tool === 'arrow') {
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
      
      // Arrowhead
      const angle = Math.atan2(y2 - y1, x2 - x1);
      ctx.beginPath();
      ctx.moveTo(x2, y2);
      ctx.lineTo(x2 - 15 * Math.cos(angle - Math.PI / 6), y2 - 15 * Math.sin(angle - Math.PI / 6));
      ctx.lineTo(x2 - 15 * Math.cos(angle + Math.PI / 6), y2 - 15 * Math.sin(angle + Math.PI / 6));
      ctx.lineTo(x2, y2);
      ctx.fillStyle = '#F87171';
      ctx.fill();
    }
  }

  function onMouseDown(e: MouseEvent) {
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    startX = (e.clientX - rect.left) * scaleX;
    startY = (e.clientY - rect.top) * scaleY;
  }

  function onMouseMove(e: MouseEvent) {
    if (!isDrawing) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const currentX = (e.clientX - rect.left) * scaleX;
    const currentY = (e.clientY - rect.top) * scaleY;
    
    redraw();
    drawShape(currentTool, startX, startY, currentX, currentY);
  }

  function onMouseUp(e: MouseEvent) {
    if (!isDrawing) return;
    isDrawing = false;
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const currentX = (e.clientX - rect.left) * scaleX;
    const currentY = (e.clientY - rect.top) * scaleY;
    
    // Only add if there is some length to it
    if (Math.abs(currentX - startX) > 2 || Math.abs(currentY - startY) > 2) {
      strokes.push({ tool: currentTool, x1: startX, y1: startY, x2: currentX, y2: currentY });
    }
    redraw();
  }

  async function copyToClipboard() {
    if (!canvas) return;
    
    // Convert canvas to blob, then get ArrayBuffer, then send to Rust
    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const buffer = await blob.arrayBuffer();
      const uint8 = new Uint8Array(buffer);
      try {
        await invoke('copy_to_clipboard', { imageBytes: Array.from(uint8) });
        // After copying, navigate back to dashboard
        window.location.href = '/';
      } catch (e) {
        console.error('Failed to copy', e);
      }
    }, 'image/png');
  }

  function cancel() {
    window.location.href = '/';
  }
</script>

<div class="preview-layout">
  <div class="toolbar">
    <div class="tools">
      <button class:active={currentTool === 'rect'} onclick={() => currentTool = 'rect'}>Rectangle</button>
      <button class:active={currentTool === 'circle'} onclick={() => currentTool = 'circle'}>Circle</button>
      <button class:active={currentTool === 'arrow'} onclick={() => currentTool = 'arrow'}>Arrow</button>
      <button onclick={() => { strokes = []; redraw(); }}>Clear</button>
    </div>
    
    <div class="actions">
      <button class="btn-cancel" onclick={cancel}>Cancel</button>
      <button class="btn-primary" onclick={copyToClipboard}>Copy Image</button>
    </div>
  </div>

  <div class="canvas-container">
    <canvas
      bind:this={canvas}
      onmousedown={onMouseDown}
      onmousemove={onMouseMove}
      onmouseup={onMouseUp}
    ></canvas>
  </div>
</div>

<style>
  .preview-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--bg);
  }

  .toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--space-3) var(--space-6);
    background: var(--surface);
    border-bottom: 1px solid var(--border);
  }

  .tools {
    display: flex;
    gap: var(--space-2);
  }

  .tools button {
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-sm);
    background: var(--elevated);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    font-size: var(--text-sm);
  }

  .tools button:hover {
    background: var(--elevated-hover);
    color: var(--text);
  }

  .tools button.active {
    background: var(--accent-subtle);
    border-color: var(--accent);
    color: var(--accent);
  }

  .actions {
    display: flex;
    gap: var(--space-3);
  }

  .actions button {
    padding: var(--space-2) var(--space-5);
    border-radius: var(--radius-md);
    font-size: var(--text-sm);
    font-weight: var(--weight-medium);
  }

  .btn-cancel {
    background: transparent;
    color: var(--text-secondary);
  }

  .btn-cancel:hover {
    color: var(--text);
  }

  .btn-primary {
    background: var(--accent);
    color: white;
  }

  .btn-primary:hover {
    background: var(--accent-hover);
  }

  .canvas-container {
    flex: 1;
    overflow: auto;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--space-6);
  }

  canvas {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    box-shadow: var(--shadow-lg);
    border-radius: var(--radius-md);
    cursor: crosshair;
  }
</style>
