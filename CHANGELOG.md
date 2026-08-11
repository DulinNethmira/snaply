# Changelog

All notable changes to Snaply are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Snaply uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.3] — 2026-08-11

### Fixed

- Replaced fake dashboard upload behavior with real file picker and drag-and-drop upload calls.
- Fixed recent share and usage loading by adding a current-user shares endpoint.
- Replaced dummy device and usage values with real local-session data.
- Prevented screenshot overlay windows from being wrapped by the authenticated app layout.
- Fixed `Ctrl+Shift+S` and clipboard share buttons by wiring them to Tauri commands.
- Fixed `.\dev.ps1 -BackendOnly` so it stays backend-only and no longer crashes on cleanup.
- Centered main app content on wide/fullscreen windows.

### Changed

- Register the Windows Explorer file context menu from the desktop app startup path.
- Added backend test coverage for current-user share listing.

## [0.1.2] — 2026-08-11

### Fixed

- Verified account creation from the installed Tauri app by allowing the `https://tauri.localhost` origin in local backend configuration and restarting the local backend.

### Changed

- Updated the desktop app to Snaply's official brand palette: cyan `#24C8DB` as the primary accent and yellow `#FFC131` as the secondary accent.
- Replaced placeholder app marks in the desktop UI with the official Snaply logo.
- Removed remaining legacy purple/gold accent colors from the desktop source theme.

## [0.1.1] — 2026-08-11

### Fixed

- Removed the duplicate Windows system tray registration so Snaply shows a single tray icon.
- Added an explicit tray icon and tooltip from the packaged app metadata.
- Allowed the installed Tauri app origin (`https://tauri.localhost`) in local backend CORS settings.
- Blocked `Ctrl+Shift+S` capture overlays when the user is not authenticated.
- Replaced failed local R2 mock uploads with real local filesystem upload/download endpoints for testing.

### Changed

- Refined the sign-in/sign-up screen with a modern animated desktop UI.

## [0.1.0] — 2026-08-09

### Initial Release

This is the first public release of Snaply.

### Added

#### Desktop Application (Windows)
- **Global hotkey capture** — Press `Ctrl+Shift+S` to open a full-screen area selection overlay across all monitors
- **Region selection** — Click and drag to select any area of the screen with pixel-precise control
- **Preview & annotation** — View your screenshot before uploading; draw, highlight, or add text
- **One-click share** — Upload the screenshot to Cloudflare R2 and receive a shareable link in seconds
- **Clipboard detection** — Press `Ctrl+Shift+V` to share an image or URL from your clipboard
- **File sharing via context menu** — Right-click any file in Windows Explorer to share it instantly with Snaply
- **Drag-and-drop uploads** — Drop files directly into the Snaply window to upload and share
- **Upload queue** — Real-time progress tracking with speed and ETA for all active uploads
- **Dashboard** — View all past uploads, share links, and usage statistics
- **Secure authentication** — JWT-based login with token rotation, stored securely in the Windows Credential Manager
- **Auto-update** — Signed updates delivered automatically via GitHub Releases
- **System tray** — Snaply runs in the background and is accessible from the system tray at all times

#### Backend API
- **FastAPI backend** — High-performance async API with full OpenAPI documentation (development mode)
- **Cloudflare R2 storage** — Direct-to-R2 uploads via short-lived presigned URLs (no file proxying)
- **Share links** — Cryptographically random tokens (256-bit entropy) with configurable expiration
- **Password-protected shares** — Optional bcrypt-hashed passwords for sensitive files
- **Usage quotas** — Per-user monthly upload limits and storage quotas
- **Rate limiting** — Per-IP rate limits on all auth endpoints
- **Automatic cleanup** — Background task removes expired shares and orphaned uploads

### Security
- JWT tokens validated against session store (logout immediately revokes access)
- No hardcoded secrets — all credentials via environment variables
- MIME type allowlist — dangerous file types rejected at the API level
- Content-Security-Policy and HSTS headers on all API responses
- OpenAPI docs disabled in production

[0.1.0]: https://github.com/DulinNethmira/snaply/releases/tag/v0.1.0
[0.1.1]: https://github.com/DulinNethmira/snaply/releases/tag/v0.1.1
[0.1.2]: https://github.com/DulinNethmira/snaply/releases/tag/v0.1.2
[0.1.3]: https://github.com/DulinNethmira/snaply/releases/tag/v0.1.3
