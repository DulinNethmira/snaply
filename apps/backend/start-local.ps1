# Snaply Local Dev Backend Starter
# ─────────────────────────────────────────────────
# Usage:   .\start-local.ps1
# Stops:   Ctrl+C
# ─────────────────────────────────────────────────

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# ── Activate local configuration ─────────────────
if (-not (Test-Path ".env.local")) {
    Write-Error ".env.local not found. Run from apps/backend/ directory."
    exit 1
}

# Back up existing .env if it looks like production (has R2 credentials)
if (Test-Path ".env") {
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "R2_ACCOUNT_ID=\S") {
        Write-Host "  Backing up production .env to .env.production" -ForegroundColor Yellow
        Copy-Item ".env" ".env.production"
    }
}

Copy-Item ".env.local" ".env" -Force
Write-Host "  [dev] Using local configuration (.env.local)" -ForegroundColor Cyan

# ── Ensure data/storage directory exists ─────────
New-Item -ItemType Directory -Force -Path "data/storage" | Out-Null

# ── Set Python path ───────────────────────────────
$env:PYTHONPATH = $ScriptDir

# ── Start uvicorn ─────────────────────────────────
Write-Host ""
Write-Host "  Snaply Backend (LOCAL MODE)" -ForegroundColor Green
Write-Host "  API:     http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Docs:    http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  Storage: $ScriptDir\data\storage" -ForegroundColor White
Write-Host "  DB:      $ScriptDir\snaply.db" -ForegroundColor White
Write-Host ""
Write-Host "  Press Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

.\venv\Scripts\uvicorn.exe app.main:app `
    --host 127.0.0.1 `
    --port 8000 `
    --reload `
    --log-level info
