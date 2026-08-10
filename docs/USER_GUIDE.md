# Snaply User Guide

**Version:** 0.1.0

---

## Installation

1. Download the latest installer from [GitHub Releases](https://github.com/DulinNethmira/snaply/releases/latest)
2. Run `Snaply_0.1.0_x64-setup.exe`
3. If Windows SmartScreen shows a warning, click **More info** → **Run anyway**
4. Follow the installation wizard
5. Snaply starts automatically and appears in the **system tray**

---

## Getting Started

### Create Your Account

On first launch, Snaply opens a login window. Click **Create account**, enter your email and a password (8+ characters), and click **Register**.

---

## Core Features

### Screenshot Capture

Press **Ctrl + Shift + S** from any application.

1. Your screen dims and a crosshair cursor appears
2. Click and drag to select the area you want to capture
3. Release the mouse to confirm the selection
4. A preview window opens — review your screenshot
5. Optionally annotate with the drawing tools
6. Click **Upload & Share** to upload to Snaply

The share link is automatically copied to your clipboard.

---

### Clipboard Sharing

Press **Ctrl + Shift + V** to instantly share whatever is in your clipboard:

- **Image** → Uploaded and shared immediately
- **URL** → Shared as a redirect link

---

### File Sharing via Right-Click

Right-click any file in Windows Explorer and select **Share with Snaply**. The file is uploaded and a share link is copied to your clipboard.

---

### Drag and Drop

Drag any file into the Snaply window to upload and share it.

---

## The Dashboard

Open Snaply from the system tray (click the icon or right-click → **Open Snaply**).

The dashboard shows:

| Column | Description |
|--------|-------------|
| **File** | Filename and file type icon |
| **Size** | File size |
| **Uploaded** | When it was uploaded |
| **Expires** | When the share link expires |
| **Status** | Active / Expired / Deleted |
| **Actions** | Copy link, Open, Delete |

---

## Share Links

### Expiration

Share links expire automatically after 24 hours by default. You can configure this in **Settings → Default expiration**.

### Revoking a Share

Click the **Delete** button next to any upload in the dashboard. The share link is immediately deactivated and the file is removed from storage.

### Password Protection

When creating a share, enable **Password protect** and set a password. Recipients will need to enter the password to view or download the file.

---

## System Tray

Snaply lives in the Windows system tray. Right-click the tray icon for options:

| Option | Action |
|--------|--------|
| **Open Snaply** | Opens the main dashboard window |
| **Quit** | Exits Snaply completely |

Left-clicking the tray icon opens or focuses the main window.

---

## Auto-Update

Snaply checks for updates automatically at startup. When an update is available, a notification appears. Snaply will download and install the update in the background. The update is applied on next launch.

Updates are cryptographically signed — only official Snaply releases are accepted.

---

## Settings

Access settings from the left sidebar in the dashboard.

| Setting | Default | Description |
|---------|---------|-------------|
| Default expiration | 24 hours | How long share links last |
| Launch at startup | On | Start Snaply with Windows |

---

## Account

### Change Password

Go to **Settings → Account → Change password**.

After changing your password, you will be logged out of all devices.

### Delete Account

Go to **Settings → Account → Delete account**. This permanently deletes your account, all uploads, and all share links. This action cannot be undone.

---

## Limits

| Resource | Limit |
|----------|-------|
| Maximum file size | 100 MB |
| Monthly uploads | 500 |
| Storage quota | 1 GB |
| Allowed file types | Images, Videos, PDFs, ZIPs, Text |

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Shift + S` | Capture screenshot (global) |
| `Ctrl + Shift + V` | Share clipboard (global) |

---

## Uninstall

Open **Settings → Apps → Installed Apps**, find **Snaply**, and click **Uninstall**. Or use **Add or Remove Programs** in the Windows Control Panel.

Uninstalling Snaply does **not** delete your account or your uploaded files. Log in to the dashboard from another device and delete your account if needed.

---

## Troubleshooting

### The hotkey doesn't work

Another application may have registered the same hotkey. Try closing applications like Snipping Tool, ShareX, or Greenshot.

### Upload fails

Check that you are logged in (tray icon shows your avatar, not a lock icon). Verify your internet connection. Check **Settings → Account** to ensure you haven't exceeded your monthly quota.

### SmartScreen warning on install

This is expected for unsigned software. Click **More info** → **Run anyway**. The Snaply installer does not contain malware. See [RELEASE.md](https://github.com/DulinNethmira/snaply/blob/main/RELEASE.md) for details on our signing roadmap.

---

## Support

- **Bug reports:** [github.com/DulinNethmira/snaply/issues](https://github.com/DulinNethmira/snaply/issues)
- **Source code:** [github.com/DulinNethmira/snaply](https://github.com/DulinNethmira/snaply)
