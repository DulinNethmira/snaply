# Changelog

All notable changes to Snaply are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Snaply uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.4] — 2026-08-12

Welcome to Snaply v0.1.4! 🚀 This release brings major quality-of-life improvements, including seamless Google authentication, automated background emails, and critical stability fixes for file uploads and sharing.

### ✨ New

- **Google OAuth Integration**: Added a sleek "Continue with Google" button to the desktop app! Instantly securely authenticate without typing passwords.
- **Deep Linking Support**: The Snaply app now registers the `snaply://` custom URI scheme on Windows to seamlessly capture OAuth tokens directly from your web browser back into the app!
- **Automated Welcome Emails**: A brand new SMTP background task system now fires off beautiful, Snaply-branded HTML welcome emails the moment you register.
- **Manual Authentication Fallback**: Having trouble with deep links? The Google login flow now includes a robust manual token fallback UI.

### 🛠 Fixed

- **Dashboard 404s**: Repaired a broken API path (`/me/shares` -> `/users/me/shares`) that was preventing the Recent Shares page from loading correctly.
- **File Upload Quotas**: The desktop app now correctly calculates the exact file size using a native Rust `get_file_size` command before uploading, fixing an issue where all files were incorrectly reported as 1MB to the backend.
- **Context Menu Sharing**: Fixed a bug where the `file-shared` event was trying to upload the Snaply executable itself instead of the intended file.
- **Recent Shares Empty State**: The "Capture Screenshot" button in the empty state now correctly triggers the screen capture overlay instead of logging to the console.

### ⚡ Improved

- **Usage Stats Resilience**: The usage statistics page now gracefully handles partial API failures, ensuring you can always see your profile stats even if your recent shares fail to load.

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
