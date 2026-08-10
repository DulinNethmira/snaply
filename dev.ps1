# Snaply Local Development Launcher
# ═══════════════════════════════════════════════════════════════
# Usage:
#   .\dev.ps1              — Start backend + desktop app
#   .\dev.ps1 -BackendOnly — Start only the backend
#   .\dev.ps1 -Reset       — Reset local database and storage
# ═══════════════════════════════════════════════════════════════

param(
    [switch]$BackendOnly,
    [switch]$Reset
)

$ErrorActionPreference = "Stop"
$Root   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "apps\backend"
$Desktop = Join-Path $Root "apps\desktop"

# ── Banner ────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ███████╗███╗   ██╗ █████╗ ██████╗ ██╗  ██╗   ██╗" -ForegroundColor Cyan
Write-Host "  ██╔════╝████╗  ██║██╔══██╗██╔══██╗██║  ╚██╗ ██╔╝" -ForegroundColor Cyan
Write-Host "  ███████╗██╔██╗ ██║███████║██████╔╝██║   ╚████╔╝ " -ForegroundColor Cyan
Write-Host "  ╚════██║██║╚██╗██║██╔══██║██╔═══╝██║    ╚██╔╝  " -ForegroundColor Cyan
Write-Host "  ███████║██║ ╚████║██║  ██║██║     ███████╗██║   " -ForegroundColor Cyan
Write-Host "  ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝   " -ForegroundColor Cyan
Write-Host "  LOCAL DEVELOPMENT MODE" -ForegroundColor Yellow
Write-Host ""

# ── Reset mode ───────────────────────────────────────────────
if ($Reset) {
    Write-Host "  Resetting local data..." -ForegroundColor Yellow
    $dbPath      = Join-Path $Backend "snaply.db"
    $storagePath = Join-Path $Backend "data\storage"

    if (Test-Path $dbPath) {
        Remove-Item $dbPath -Force
        Write-Host "  Deleted: snaply.db" -ForegroundColor Red
    }
    if (Test-Path $storagePath) {
        Remove-Item $storagePath -Recurse -Force
        Write-Host "  Deleted: data/storage/" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "  Reset complete. Run .\dev.ps1 to start fresh." -ForegroundColor Green
    exit 0
}

# ── Check prerequisites ───────────────────────────────────────
$uvicorn = Join-Path $Backend "venv\Scripts\uvicorn.exe"
if (-not (Test-Path $uvicorn)) {
    Write-Error "uvicorn not found at $uvicorn`nRun: cd apps\backend && python -m venv venv && .\venv\Scripts\pip install -r requirements.txt"
}

if (-not $BackendOnly) {
    $npm = Get-Command npm -ErrorAction SilentlyContinue
    if (-not $npm) {
        Write-Error "npm not found. Install Node.js from https://nodejs.org"
    }
}

# ── Activate local .env ───────────────────────────────────────
$envLocal  = Join-Path $Backend ".env.local"
$envTarget = Join-Path $Backend ".env"
$envProd   = Join-Path $Backend ".env.production"

if (-not (Test-Path $envLocal)) {
    Write-Error ".env.local not found at $envLocal"
}

if (Test-Path $envTarget) {
    $existing = Get-Content $envTarget -Raw
    if ($existing -match "R2_ACCOUNT_ID=\S") {
        Write-Host "  Backing up production .env to .env.production" -ForegroundColor Yellow
        Copy-Item $envTarget $envProd -Force
    }
}
Copy-Item $envLocal $envTarget -Force
Write-Host "  [✓] Local config activated (.env.local)" -ForegroundColor Green

# ── Ensure storage directory exists ──────────────────────────
New-Item -ItemType Directory -Force -Path (Join-Path $Backend "data\storage") | Out-Null

# ── Start backend ─────────────────────────────────────────────
Write-Host "  [*] Starting backend..." -ForegroundColor Cyan
$env:PYTHONPATH = $Backend

$backendProc = Start-Process -FilePath $uvicorn `
    -ArgumentList "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload", "--log-level", "info" `
    -WorkingDirectory $Backend `
    -PassThru `
    -NoNewWindow

Write-Host "  [✓] Backend PID $($backendProc.Id)" -ForegroundColor Green

# ── Wait for health endpoint ──────────────────────────────────
Write-Host "  [*] Waiting for backend to be ready..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
}

if (-not $ready) {
    Write-Host "  [!] Backend did not become ready in 15s. Check output above." -ForegroundColor Red
    $backendProc | Stop-Process -Force
    exit 1
}

Write-Host "  [✓] Backend ready at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "      Docs: http://127.0.0.1:8000/docs" -ForegroundColor DarkGray

if ($BackendOnly) {
    Write-Host ""
    Write-Host "  Backend running. Press Ctrl+C to stop." -ForegroundColor Yellow
    Wait-Process -Id $backendProc.Id
    exit 0
}

# ── Start desktop app ─────────────────────────────────────────
Write-Host "  [*] Starting Snaply desktop app..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  ┌─────────────────────────────────────────┐" -ForegroundColor DarkGray
Write-Host "  │  API:      http://127.0.0.1:8000        │" -ForegroundColor White
Write-Host "  │  Docs:     http://127.0.0.1:8000/docs   │" -ForegroundColor White
Write-Host "  │  Storage:  apps/backend/data/storage/   │" -ForegroundColor White
Write-Host "  │  Database: apps/backend/snaply.db        │" -ForegroundColor White
Write-Host "  └─────────────────────────────────────────┘" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Press Ctrl+C to stop both backend and desktop." -ForegroundColor DarkGray
Write-Host ""

try {
    Set-Location $Desktop
    npm run tauri dev
} finally {
    # Always clean up backend when desktop exits
    Write-Host ""
    Write-Host "  Stopping backend (PID $($backendProc.Id))..." -ForegroundColor Yellow
    if (-not $backendProc.HasExited) {
        $backendProc | Stop-Process -Force
    }
    Write-Host "  Done." -ForegroundColor Green
}
