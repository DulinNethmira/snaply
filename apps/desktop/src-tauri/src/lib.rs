use std::collections::HashMap;
use std::io::Cursor;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicBool, Ordering};

use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, TrayIconBuilder, TrayIconEvent},
    Manager, WebviewWindowBuilder, Emitter,
};
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Modifiers, Shortcut, ShortcutState};
use xcap::Monitor as XcapMonitor;
use image::DynamicImage;
use image::codecs::png::{PngEncoder, CompressionType, FilterType};
use arboard::{Clipboard, ImageData};

use winreg::enums::*;
use winreg::RegKey;

use tokio::fs::File;
use tokio::io::AsyncReadExt;

use tauri_plugin_updater::UpdaterExt;

struct AppState {
    captures: Mutex<HashMap<String, Vec<u8>>>,
    uploads: Mutex<HashMap<String, Arc<AtomicBool>>>,
}

#[tauri::command]
fn get_monitor_capture(app: tauri::AppHandle, monitor_name: String) -> Result<Vec<u8>, String> {
    let state = app.state::<AppState>();
    let captures = state.captures.lock().unwrap();
    if let Some(data) = captures.get(&monitor_name) {
        Ok(data.clone())
    } else {
        Err("Capture not found for monitor".to_string())
    }
}

#[tauri::command]
fn get_all_monitors(app: tauri::AppHandle) -> Result<Vec<String>, String> {
    let mut names = Vec::new();
    if let Ok(monitors) = app.available_monitors() {
        for m in monitors {
            if let Some(name) = m.name() {
                names.push(name.to_string());
            }
        }
    }
    Ok(names)
}

#[tauri::command]
fn crop_and_preview(
    app: tauri::AppHandle,
    monitor_name: String,
    x: u32,
    y: u32,
    width: u32,
    height: u32,
) -> Result<(), String> {
    let state = app.state::<AppState>();
    let png_bytes = {
        let captures = state.captures.lock().unwrap();
        captures.get(&monitor_name).cloned().ok_or("Capture not found")?
    };

    let img = image::load_from_memory(&png_bytes).map_err(|e| e.to_string())?;
    let cropped = img.crop_imm(x, y, width, height);

    let mut out_bytes = Vec::new();
    let mut cursor = Cursor::new(&mut out_bytes);
    let encoder = PngEncoder::new_with_quality(
        &mut cursor,
        CompressionType::Fast,
        FilterType::NoFilter,
    );
    cropped
        .write_with_encoder(encoder)
        .map_err(|e| e.to_string())?;

    {
        let mut captures = state.captures.lock().unwrap();
        captures.insert("preview".to_string(), out_bytes);
    }

    close_all_overlays(&app);

    if let Some(main_win) = app.get_webview_window("main") {
        let _ = main_win.show();
        let _ = main_win.set_focus();
        let _ = main_win.eval("window.location.href = '/preview';");
    }

    Ok(())
}

#[tauri::command]
fn cancel_capture(app: tauri::AppHandle) {
    close_all_overlays(&app);
}

fn close_all_overlays(app: &tauri::AppHandle) {
    for (label, window) in app.webview_windows() {
        if label.starts_with("overlay_") {
            let _ = window.close();
        }
    }
}

#[tauri::command]
fn copy_to_clipboard(app: tauri::AppHandle, image_bytes: Vec<u8>) -> Result<(), String> {
    let img = image::load_from_memory(&image_bytes).map_err(|e| e.to_string())?;
    let rgba = img.into_rgba8();
    let (w, h) = rgba.dimensions();
    let img_data = ImageData {
        width: w as usize,
        height: h as usize,
        bytes: rgba.into_raw().into(),
    };

    let mut clipboard = Clipboard::new().map_err(|e| e.to_string())?;
    clipboard.set_image(img_data).map_err(|e| e.to_string())?;

    use tauri_plugin_notification::NotificationExt;
    let _ = app.notification()
        .builder()
        .title("Screenshot Captured")
        .body("Image copied to clipboard.")
        .show();

    Ok(())
}

fn trigger_capture(app: &tauri::AppHandle) {
    // ── Auth guard ────────────────────────────────────────────────────
    // Don't open the capture overlay when the user hasn't logged in yet.
    // Instead, just focus the main window so they can authenticate.
    let is_authenticated = keyring::Entry::new("Snaply", "AuthToken")
        .ok()
        .and_then(|entry| entry.get_password().ok())
        .map(|token| !token.is_empty())
        .unwrap_or(false);

    if !is_authenticated {
        if let Some(win) = app.get_webview_window("main") {
            let _ = win.show();
            let _ = win.set_focus();
        }
        return;
    }
    // ──────────────────────────────────────────────────────────────────

    println!("Triggering capture...");
    let xcap_monitors = XcapMonitor::all().unwrap_or_default();
    let mut capture_map = HashMap::new();

    for xcap_m in xcap_monitors {
        if let Ok(img) = xcap_m.capture_image() {
            let mut bytes = Vec::new();
            let mut cursor = Cursor::new(&mut bytes);
            let encoder = PngEncoder::new_with_quality(
                &mut cursor,
                CompressionType::Fast,
                FilterType::NoFilter,
            );
            if DynamicImage::ImageRgba8(img).write_with_encoder(encoder).is_ok() {
                capture_map.insert(xcap_m.name().unwrap_or_default(), bytes);
            }
        }
    }

    {
        let state = app.state::<AppState>();
        let mut captures = state.captures.lock().unwrap();
        *captures = capture_map;
    }

    if let Ok(monitors) = app.available_monitors() {
        for (i, monitor) in monitors.iter().enumerate() {
            let label = format!("overlay_{}", i);
            let pos = monitor.position();
            let size = monitor.size();
            
            let name = monitor.name().map(|s| s.as_str()).unwrap_or("");
            let url = format!("/overlay?monitor={}", urlencoding::encode(name));

            if let Ok(window) = WebviewWindowBuilder::new(app, &label, tauri::WebviewUrl::App(url.into()))
                .title("Snaply Selection")
                .decorations(false)
                .transparent(true)
                .always_on_top(true)
                .skip_taskbar(true)
                .resizable(false)
                .position(pos.x as f64, pos.y as f64)
                .inner_size(size.width as f64, size.height as f64)
                .build() 
            {
                let _ = window.show();
            }
        }
    }
}


// --------------------------------------------------------
// Phase 7 Features: Auth & Cloud Integration
// --------------------------------------------------------

fn get_auth_entry() -> Result<keyring::Entry, String> {
    keyring::Entry::new("Snaply", "AuthToken").map_err(|e| e.to_string())
}

#[tauri::command]
fn set_auth_token(token: String) -> Result<(), String> {
    let entry = get_auth_entry()?;
    entry.set_password(&token).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn get_auth_token() -> Result<Option<String>, String> {
    let entry = get_auth_entry()?;
    match entry.get_password() {
        Ok(token) => Ok(Some(token)),
        Err(keyring::Error::NoEntry) => Ok(None),
        Err(e) => Err(e.to_string()),
    }
}

#[tauri::command]
fn delete_auth_token() -> Result<(), String> {
    let entry = get_auth_entry()?;
    match entry.delete_password() {
        Ok(_) => Ok(()),
        Err(keyring::Error::NoEntry) => Ok(()), // Already deleted
        Err(e) => Err(e.to_string()),
    }
}

// --------------------------------------------------------
// Phase 3 Features: Uploads, Clipboard, Context Menu
// --------------------------------------------------------

#[tauri::command]
fn register_context_menu() -> Result<(), String> {
    let exe_path = std::env::current_exe().map_err(|e| e.to_string())?;
    let exe_path_str = exe_path.to_str().unwrap_or_default();
    
    let hkcu = RegKey::predef(HKEY_CURRENT_USER);
    // Add to all files context menu
    let (shell_key, _) = hkcu.create_subkey(r"Software\Classes\*\shell\Snaply").map_err(|e| e.to_string())?;
    shell_key.set_value("", &"Share with Snaply").map_err(|e| e.to_string())?;
    
    let (command_key, _) = shell_key.create_subkey("command").map_err(|e| e.to_string())?;
    let command_val = format!("\"{}\" \"%1\"", exe_path_str);
    command_key.set_value("", &command_val).map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn upload_file_to_r2(app: tauri::AppHandle, id: String, path: String, url: String, mime_type: String) -> Result<(), String> {
    let cancel_flag = Arc::new(AtomicBool::new(false));
    {
        let state = app.state::<AppState>();
        state.uploads.lock().unwrap().insert(id.clone(), cancel_flag.clone());
    }

    let file = File::open(&path).await.map_err(|e| e.to_string())?;
    let total_bytes = file.metadata().await.map_err(|e| e.to_string())?.len();

    let app_clone = app.clone();
    let id_clone = id.clone();
    let cancel_clone = cancel_flag.clone();
    let path_clone = path.clone();

    let stream = async_stream::stream! {
        let mut file = File::open(&path_clone).await.map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
        let mut buffer = vec![0; 1024 * 1024]; // 1MB chunks
        let mut uploaded_bytes = 0;
        loop {
            if cancel_clone.load(Ordering::SeqCst) {
                yield Err(std::io::Error::new(std::io::ErrorKind::Interrupted, "Upload cancelled"));
                return;
            }
            match file.read(&mut buffer).await {
                Ok(0) => break,
                Ok(n) => {
                    uploaded_bytes += n as u64;
                    let _ = app_clone.emit("upload-progress", serde_json::json!({
                        "id": id_clone,
                        "uploaded": uploaded_bytes,
                        "total": total_bytes,
                    }));
                    yield Ok(bytes::Bytes::copy_from_slice(&buffer[..n]));
                },
                Err(e) => {
                    yield Err(e);
                    return;
                }
            }
        }
    };

    let client = reqwest::Client::new();
    let res = client.put(&url)
        .header("Content-Type", mime_type)
        .header("Content-Length", total_bytes)
        .body(reqwest::Body::wrap_stream(stream))
        .send()
        .await
        .map_err(|e| e.to_string())?;

    {
        let state = app.state::<AppState>();
        state.uploads.lock().unwrap().remove(&id);
    }

    if res.status().is_success() {
        Ok(())
    } else {
        Err(format!("Upload failed with status: {}", res.status()))
    }
}

#[tauri::command]
async fn upload_bytes_to_r2(app: tauri::AppHandle, id: String, capture_key: String, url: String, mime_type: String) -> Result<(), String> {
    let bytes = {
        let state = app.state::<AppState>();
        let captures = state.captures.lock().unwrap();
        captures.get(&capture_key).cloned().ok_or("Data not found in memory")?
    };
    
    let total_bytes = bytes.len() as u64;
    
    // For in-memory data, just simulate immediate progress update and upload all at once
    let _ = app.emit("upload-progress", serde_json::json!({
        "id": id,
        "uploaded": total_bytes,
        "total": total_bytes,
    }));
    
    let client = reqwest::Client::new();
    let res = client.put(&url)
        .header("Content-Type", mime_type)
        .header("Content-Length", total_bytes)
        .body(bytes)
        .send()
        .await
        .map_err(|e| e.to_string())?;

    if res.status().is_success() {
        Ok(())
    } else {
        Err(format!("Upload failed with status: {}", res.status()))
    }
}

#[tauri::command]
fn cancel_upload(app: tauri::AppHandle, id: String) {
    let state = app.state::<AppState>();
    let uploads = state.uploads.lock().unwrap();
    if let Some(flag) = uploads.get(&id) {
        flag.store(true, Ordering::SeqCst);
    }
}

fn check_clipboard(app: &tauri::AppHandle) {
    if let Ok(mut clipboard) = Clipboard::new() {
        if let Ok(img) = clipboard.get_image() {
            let mut out_bytes = Vec::new();
            if let Some(dynamic) = image::RgbaImage::from_raw(img.width as u32, img.height as u32, img.bytes.into_owned()) {
                let mut cursor = Cursor::new(&mut out_bytes);
                let encoder = PngEncoder::new_with_quality(
                    &mut cursor,
                    CompressionType::Fast,
                    FilterType::NoFilter,
                );
                if image::DynamicImage::ImageRgba8(dynamic).write_with_encoder(encoder).is_ok() {
                    let state = app.state::<AppState>();
                    state.captures.lock().unwrap().insert("clipboard_image".to_string(), out_bytes);
                    let _ = app.emit("clipboard-detected", "image");
                }
            }
        } else if let Ok(text) = clipboard.get_text() {
            let state = app.state::<AppState>();
            state.captures.lock().unwrap().insert("clipboard_text".to_string(), text.as_bytes().to_vec());
            if text.starts_with("http://") || text.starts_with("https://") {
                let _ = app.emit("clipboard-detected", "url");
            } else {
                let _ = app.emit("clipboard-detected", "text");
            }
        }
    }
}

#[tauri::command]
async fn check_update(app: tauri::AppHandle) -> Result<bool, String> {
    match app.updater() {
        Ok(updater) => match updater.check().await {
            Ok(Some(update)) => {
                let version = update.version.clone();
                let _ = app.emit("update-available", version);
                Ok(true)
            }
            Ok(None) => Ok(false),
            Err(e) => Err(format!("Update check failed: {e}")),
        },
        Err(e) => Err(format!("Updater not available: {e}")),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, argv, _cwd| {
            // Forward CLI args to the frontend
            let _ = app.emit("file-shared", argv);
        }))
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_updater::Builder::new().build())
        .manage(AppState {
            captures: Mutex::new(HashMap::new()),
            uploads: Mutex::new(HashMap::new()),
        })
        .setup(|app| {
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let open_i = MenuItem::with_id(app, "open", "Open Snaply", true, None::<&str>)?;
            let label_i = MenuItem::with_id(app, "snaply", "Snaply", false, None::<&str>)?;
            let menu = Menu::with_items(app, &[&label_i, &open_i, &quit_i])?;

            let mut tray_builder = TrayIconBuilder::new()
                .menu(&menu)
                .tooltip("Snaply - Capture. Share. Done.")
                .show_menu_on_left_click(false);

            if let Some(icon) = app.default_window_icon().cloned() {
                tray_builder = tray_builder.icon(icon);
            }

            tray_builder
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        app.exit(0);
                    }
                    "open" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: tauri::tray::MouseButtonState::Up,
                        ..
                    } = event
                    {
                        if let Some(window) = tray.app_handle().get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            // Register global shortcuts
            let ctrl_shift_s = Shortcut::new(Some(Modifiers::CONTROL | Modifiers::SHIFT), Code::KeyS);
            let ctrl_shift_v = Shortcut::new(Some(Modifiers::CONTROL | Modifiers::SHIFT), Code::KeyV);
            let app_handle = app.handle().clone();
            let app_handle_clone = app_handle.clone();
            
            app_handle.plugin(
                tauri_plugin_global_shortcut::Builder::new()
                    .with_handler(move |_app, shortcut, event| {
                        if event.state() == ShortcutState::Pressed {
                            if shortcut == &ctrl_shift_s {
                                trigger_capture(&app_handle_clone);
                            } else if shortcut == &ctrl_shift_v {
                                check_clipboard(&app_handle_clone);
                            }
                        }
                    })
                    .build(),
            )?;

            app.global_shortcut().register(ctrl_shift_s)?;
            app.global_shortcut().register(ctrl_shift_v)?;
            
            // Check args on initial launch for context menu files
            let args: Vec<String> = std::env::args().collect();
            if args.len() > 1 {
                // Ignore first arg (executable path), the rest are file paths
                let _ = app.emit("file-shared", args);
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                if window.label() == "main" {
                    let _ = window.hide();
                    api.prevent_close();
                }
            }
        })
        .invoke_handler(tauri::generate_handler![
            get_monitor_capture,
            get_all_monitors,
            crop_and_preview,
            cancel_capture,
            copy_to_clipboard,
            register_context_menu,
            upload_file_to_r2,
            upload_bytes_to_r2,
            cancel_upload,
            set_auth_token,
            get_auth_token,
            delete_auth_token,
            check_update
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
