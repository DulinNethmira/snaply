# Snaply

**Capture. Share. Done.**

Snaply is a lightweight Windows desktop application for instant screenshot sharing. Press a hotkey, select an area, and get a shareable link — in under 3 seconds.

[![Release](https://img.shields.io/github/v/release/DulinNethmira/snaply?style=flat-square&color=6366f1)](https://github.com/DulinNethmira/snaply/releases/latest)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-0078d4?style=flat-square&logo=windows)](https://github.com/DulinNethmira/snaply/releases/latest)

---

## Download

**[→ Download Snaply for Windows](https://github.com/DulinNethmira/snaply/releases/latest)**

---

## Features

- **Global hotkey** — `Ctrl+Shift+S` to capture any region, instantly
- **Instant share** — Uploads to Cloudflare R2 and copies a link to your clipboard
- **Clipboard sharing** — `Ctrl+Shift+V` to share the current clipboard image or URL
- **File sharing** — Right-click any file → *Share with Snaply*
- **Expiring links** — Links expire automatically (configurable)
- **Password protection** — Protect sensitive shares with a password
- **System tray** — Runs quietly in the background, always ready
- **Auto-update** — Receives signed updates automatically
- **Secure** — JWT auth, R2 presigned URLs, no file proxying

---

## Architecture

```
┌─────────────────────────┐     ┌────────────────────┐     ┌─────────────────┐
│  Desktop App (Tauri 2)  │────▶│  Backend (FastAPI)  │────▶│  Cloudflare R2  │
│  SvelteKit + Rust       │     │  SQLite + slowapi   │     │  Object Storage │
└─────────────────────────┘     └────────────────────┘     └─────────────────┘
         │ Ctrl+Shift+S                    │
         ▼                                 ▼
   Screenshot capture              Auth, quotas,
   Region selection                share tokens
   Annotation overlay              Presigned URLs
```

**Upload flow:** Desktop → requests presigned URL from backend → uploads directly to R2 → backend confirms → share link generated.

No file content ever passes through the backend server.

---

## Development Setup

### Prerequisites

- [Node.js 20+](https://nodejs.org/)
- [Rust (stable)](https://rustup.rs/)
- [Python 3.11+](https://python.org/)

### Desktop App

```sh
cd apps/desktop
npm install
npm run tauri dev
```

### Backend API

```sh
cd apps/backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set SECRET_KEY
uvicorn app.main:app --reload
```

---

## Project Structure

```
snaply/
├── apps/
│   ├── desktop/              # Tauri 2 + SvelteKit desktop app
│   │   ├── src/              # SvelteKit frontend
│   │   └── src-tauri/        # Rust backend (Tauri commands)
│   └── backend/              # FastAPI REST API
│       └── app/
│           ├── api/          # Route handlers
│           ├── core/         # Security, config, storage
│           ├── db/           # SQLAlchemy session + models
│           └── models/       # ORM models
├── docs/                     # Landing page (GitHub Pages)
├── .github/workflows/        # CI/CD pipelines
├── CHANGELOG.md
├── RELEASE.md                # Release & code signing guide
└── LICENSE
```

---

## Releasing

See [RELEASE.md](RELEASE.md) for the full release process, including:
- Generating updater signing keys
- Configuring GitHub Secrets
- Purchasing a code signing certificate
- Triggering a release via git tag

---

## License

MIT © 2026 Snaply
