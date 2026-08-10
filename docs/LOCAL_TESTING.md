# Snaply Local Testing Guide

This guide explains how to run the **complete Snaply application locally** on Windows for development and testing — with no cloud infrastructure required.

---

## Architecture (Local Mode)

```
Snaply Desktop App (Tauri)
        │
        │  HTTP  (http://127.0.0.1:8000)
        ▼
FastAPI Backend (uvicorn)
        │
        ├── SQLite  (apps/backend/snaply.db)
        │
        └── LocalStorageProvider
                │
                └── apps/backend/data/storage/
```

**What changes in local mode vs production:**

| Component | Production | Local |
|---|---|---|
| Storage | Cloudflare R2 | Local filesystem (`data/storage/`) |
| Database | SQLite (same) | SQLite (same) |
| Share URLs | `https://api.snaply.app/s/<token>` | `http://127.0.0.1:8000/s/<token>` |
| Upload URLs | R2 presigned PUT | `http://127.0.0.1:8000/local-storage/upload/<key>` |
| File serving | R2 presigned GET | `http://127.0.0.1:8000/local-storage/files/<key>` |
| API docs | Hidden | `http://127.0.0.1:8000/docs` |

---

## Prerequisites

- Python 3.11+ with a virtual environment in `apps/backend/venv/`
- Node.js 20+ and npm
- Rust toolchain (for `tauri dev`)

If you haven't set up the backend venv:
```powershell
cd apps/backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

---

## Quick Start

From the **repository root**:

```powershell
.\dev.ps1
```

This will:
1. Activate local configuration (`.env.local`)
2. Create `data/storage/` directory
3. Start the backend at `http://127.0.0.1:8000`
4. Wait for the health endpoint to respond
5. Launch the Snaply desktop app in dev mode

---

## Commands

### Start local environment
```powershell
.\dev.ps1
```

### Start backend only (no desktop app)
```powershell
.\dev.ps1 -BackendOnly
```

### Reset local data (delete DB + all stored files)
```powershell
.\dev.ps1 -Reset
```

### Stop
Press **Ctrl+C** in the terminal running `dev.ps1`. Both the backend and desktop app will stop.

---

## URLs & Paths

| Resource | Location |
|---|---|
| API base URL | `http://127.0.0.1:8000/api/v1` |
| API docs (Swagger) | `http://127.0.0.1:8000/docs` |
| Share page | `http://127.0.0.1:8000/s/<token>` |
| Local database | `apps/backend/snaply.db` |
| Local file storage | `apps/backend/data/storage/` |
| Local config | `apps/backend/.env.local` |

---

## Full End-to-End Test Checklist

Run through each step to verify the complete workflow:

| # | Step | How to verify |
|---|---|---|
| 1 | Start Snaply | Run `.\dev.ps1` — no errors |
| 2 | Start backend | Backend shows ✓ ready in `dev.ps1` output |
| 3 | Register | Create new account in the app UI |
| 4 | Login | Log in with the credentials you just registered |
| 5 | Capture screenshot | Press `Ctrl+Shift+S`, select an area |
| 6 | Preview | Preview window shows the captured area |
| 7 | Annotate | (if annotation is supported) |
| 8 | Upload screenshot | Confirm upload completes (status = Complete) |
| 9 | Generate share link | Link is shown after upload |
| 10 | Copy share link | Click copy — `http://127.0.0.1:8000/s/<token>` |
| 11 | Open share link | Open link in browser |
| 12 | View shared content | Share page renders with image preview |
| 13 | Download content | Click Download on share page |
| 14 | Verify downloaded file | File opens correctly |
| 15 | View recent shares | Check Recent Shares in the app |
| 16 | Delete a share | Delete from app UI |
| 17 | Verify deletion | Share link now returns 404 |
| 18 | Upload a file | Drag & drop a `.pdf` or `.zip` file |
| 19 | Upload an image | Drag & drop a `.png` or `.jpg` |
| 20 | Upload a video | Drag & drop a `.mp4` |
| 21 | Test clipboard sharing | Copy image to clipboard, Snaply prompts upload |
| 22 | Test expiration | Set expiration, wait, verify link expires |
| 23 | Logout | Use logout in settings |
| 24 | Login again | Log back in with same credentials |
| 25 | Verify data persists | Previous shares should still be listed |
| 26 | Test invalid share | Open `http://127.0.0.1:8000/s/invalid-token` → 404 page |
| 27 | Test backend unavailable | Stop backend, try upload → app shows error |
| 28 | Restart backend | Start backend again |
| 29 | Verify recovery | App reconnects, uploads work again |

---

## Switching Back to Production Configuration

To restore production config, either:

**Option A — Restore backup (if `dev.ps1` created one):**
```powershell
Copy-Item apps\backend\.env.production apps\backend\.env -Force
```

**Option B — Restore from version control:**
```powershell
git checkout apps/backend/.env
```

> [!WARNING]
> Never commit `apps/backend/.env` to git. It is listed in `.gitignore`.
> The local config (`.env.local`) IS committed since it contains no secrets.

---

## Clearing Local Data

### Clear uploaded files only
```powershell
Remove-Item apps\backend\data\storage\* -Recurse -Force
```

### Clear database only
```powershell
Remove-Item apps\backend\snaply.db -Force
```

### Clear everything (full reset)
```powershell
.\dev.ps1 -Reset
```

---

## Storage Location

In local mode, files are stored at:
```
apps/backend/data/storage/users/<user-id>/objects/<uuid>
```

This mirrors the R2 key structure (`users/{user_id}/objects/{object_id}`) so switching between providers requires only a config change.

---

## Known Limitations

1. **No HTTPS in local mode** — Share links are `http://` only. This is expected for local testing.
2. **No CDN** — Large files are served directly by uvicorn. Suitable for testing, not production load.
3. **Single worker** — The local backend runs with `--reload` (single process). Fine for dev.
4. **Token expiry** — JWT tokens expire in 60 minutes by default. Re-login if needed.
5. **Rate limiting** — The 5/minute rate limit on login/register is still enforced locally.
6. **Auto-updater** — Not functional in `tauri dev` mode (only in production builds).

---

## Environment Variables Reference

All local settings are in `apps/backend/.env.local`:

| Variable | Local Value | Description |
|---|---|---|
| `SNAPLY_ENV` | `development` | Environment identifier |
| `STORAGE_PROVIDER` | `local` | Use `LocalStorageProvider` |
| `LOCAL_STORAGE_DIR` | `data/storage` | Where files are stored |
| `DEBUG` | `true` | Enable API docs, verbose errors |
| `SECRET_KEY` | (dev key) | JWT signing key |
| `SQLALCHEMY_DATABASE_URI` | `sqlite+aiosqlite:///./snaply.db` | Local SQLite |
| `BACKEND_CORS_ORIGINS` | localhost origins | Allowed CORS origins |
| `R2_*` | (empty) | Leave empty — R2 not used in local mode |
