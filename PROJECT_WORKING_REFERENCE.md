# Media Controller - Full Working Reference

Generated: 2026-03-28

## 1) Project Purpose

This project runs a web-controlled media slideshow system for Raspberry Pi (or Linux desktop).  
It provides:
- A Flask web dashboard to upload/delete media and control playback.
- A slideshow engine that plays photos and videos fullscreen.
- Safe process and file handling (PID file, pending delete queue).
- Shop-ready deployment using a systemd service script.

## 2) High-Level Runtime Flow

1. `python app.py` starts Flask web server.
2. User opens `http://<device-ip>:5000`.
3. User presses `START`.
4. Flask starts `python slideshow.py` in a separate process.
5. `slideshow.py` loops through `photos/` and `videos/`.
6. User can `STOP`, upload media, delete media, and change interval.

## 3) Folder Structure and Working

```text
Py/
  .gitignore
  app.py
  slideshow.py
  install_shop_service.sh
  README_RASPBERRY_PI.md
  requirements.txt
  config.json
  pending_delete.json
  media_controller/
    __init__.py
    constants.py
    config_store.py
    pending_store.py
    process_manager.py
    networking.py
    web.py
    slideshow_runner.py
    templates/
      index.html
  photos/
  videos/
```

### `photos/` folder
- Purpose: Stores uploaded image files.
- Used by:
  - Web upload route (`/upload`) for writing images.
  - Slideshow engine for image playback.

### `videos/` folder
- Purpose: Stores uploaded video files.
- Used by:
  - Web upload route (`/upload`) for writing videos.
  - Slideshow engine for video playback.

### `media_controller/` package
- Purpose: Core project logic split into clean modules.
- Benefit: Easier maintenance, testing, and scaling.

## 4) File-by-File Working

### File: `app.py`
Purpose:
- Minimal entrypoint for the web app.

Working:
- Imports `run` from `media_controller.web`.
- Calls `run()` when executed directly.

Functions:
- No custom function; direct entrypoint.

---

### File: `slideshow.py`
Purpose:
- Minimal entrypoint for slideshow process.

Working:
- Imports `run_slideshow` from `media_controller.slideshow_runner`.
- Calls `run_slideshow()` when executed directly.

Functions:
- No custom function; direct entrypoint.

---

### File: `media_controller/__init__.py`
Purpose:
- Package export file.

Working:
- Re-exports `create_app` and `run` for convenience.

Functions:
- No function definitions.

---

### File: `media_controller/constants.py`
Purpose:
- Centralized constants and runtime file/folder paths.

Key constants:
- `PROJECT_ROOT`
- `PHOTO_FOLDER`, `VIDEO_FOLDER`
- `CONFIG_FILE`, `PENDING_DELETE_FILE`
- `SLIDESHOW_PID_FILE`
- `SLIDESHOW_OUT_LOG_FILE`, `SLIDESHOW_ERR_LOG_FILE`, `SLIDESHOW_LOG_FILE`
- `ALLOWED_PHOTO_EXTS`, `ALLOWED_VIDEO_EXTS`

Functions:
- `ensure_runtime_dirs()`
  - Creates `photos/` and `videos/` folders if missing.

---

### File: `media_controller/config_store.py`
Purpose:
- Read/write runtime config from `config.json`.

Functions:
- `get_config()`
  - Loads JSON config.
  - Validates `photo_interval`.
  - Returns default `{"photo_interval": 5}` if file is missing/invalid.

- `save_config(config)`
  - Writes config dictionary to `config.json`.

---

### File: `media_controller/pending_store.py`
Purpose:
- Manage pending-delete queue for files that cannot be deleted immediately.

Why needed:
- During playback, delete operations can fail due to file lock.
- Failed deletes are queued and retried safely.

Functions:
- `norm_path(path)`
  - Returns normalized absolute path.

- `load_pending()`
  - Reads `pending_delete.json`.
  - Returns a set of pending file paths.

- `save_pending(pending)`
  - Atomically writes pending set to JSON using temp file + `os.replace`.

- `add_pending(path)`
  - Adds a file to pending queue.

- `remove_pending(path)`
  - Removes a file from pending queue.

- `is_pending(path)`
  - Checks if file is in pending queue.

- `try_clear_pending(path)`
  - If file is pending, tries to delete it and remove queue entry.

- `is_within(base_folder, path)`
  - Security check to ensure path stays inside allowed folder.

- `resolve_media_path(media_type, filename)`
  - Converts route params into safe absolute path inside `photos/` or `videos/`.

---

### File: `media_controller/process_manager.py`
Purpose:
- Handle slideshow process lifecycle and PID tracking.

Functions:
- `write_pid(pid)`
  - Stores slideshow PID in `slideshow.pid` atomically.

- `read_pid()`
  - Reads PID from `slideshow.pid` (returns `None` if invalid/missing).

- `clear_pid()`
  - Removes `slideshow.pid`.

- `pid_exists(pid)`
  - Cross-platform check if process exists.
  - Windows: uses `tasklist`.
  - POSIX: uses `os.kill(pid, 0)`.

- `kill_pid(pid)`
  - Terminates process.
  - Windows: `taskkill /F /T`.
  - POSIX: tries process-group kill (`SIGTERM` then `SIGKILL`), fallback single PID.

- `is_running(local_process=None)`
  - Returns running status from in-memory process or PID file.
  - Clears stale PID file automatically.

---

### File: `media_controller/networking.py`
Purpose:
- Detect LAN IP for easy phone access URL.

Functions:
- `get_lan_ip()`
  - Best-effort local IP detection by opening UDP socket to `8.8.8.8`.
  - Returns `127.0.0.1` on failure.

---

### File: `media_controller/web.py`
Purpose:
- Main Flask app, routes, upload/delete/config APIs, slideshow process control.

Main functions:

- `_slideshow_env()`
  - Creates environment for slideshow process.
  - On Linux, sets `DISPLAY=:0` if missing (important for Raspberry Pi display output).

- `create_app()`
  - Builds Flask app instance.
  - Ensures runtime folders.
  - Registers all routes.
  - Maintains local process state: `state["slideshow_process"]`.

  Routes inside `create_app()`:
  - `index()` -> `GET /`
    - Loads photo/video filenames and app status.
    - Renders `templates/index.html`.

  - `start_slideshow()` -> `POST /start`
    - Prevents duplicate start if PID already active.
    - Launches `slideshow.py` process.
    - Logs stdout/stderr to `slideshow.out.log` and `slideshow.err.log`.
    - Stores PID and clears stale PID on instant crash.

  - `stop_slideshow()` -> `POST /stop`
    - Stops in-memory slideshow process if running.
    - Stops PID file process if exists.
    - Clears PID file.

  - `upload_file()` -> `POST /upload`
    - Accepts one file from form.
    - Validates extension and routes to `photos/` or `videos/`.
    - Saves file and clears pending-delete marker for that path.

  - `set_interval()` -> `POST /set_interval`
    - Reads interval from form.
    - Validates minimum `1`.
    - Saves config.

  - `delete_file(media_type, filename)` -> `POST /delete/<media_type>/<filename>`
    - Resolves safe path.
    - Attempts delete.
    - On failure, adds file to pending queue.

- `run()`
  - Starts Flask app with `HOST` and `PORT` environment support.
  - Prints phone-open URL when host is `0.0.0.0`.

---

### File: `media_controller/slideshow_runner.py`
Purpose:
- Fullscreen slideshow playback engine.

Playback strategy:
- Photos:
  - Primary: pygame fullscreen rendering.
  - Fallback: ffplay if pygame render fails.
- Videos:
  - ffplay fullscreen with low-delay flags.

Functions:
- `get_interval()`
  - Returns validated `photo_interval` from config.

- `_log(msg)`
  - Appends internal slideshow logs to `slideshow.log`.

- `_list_media()`
  - Lists files from `photos/` + `videos/`.
  - Keeps only allowed extensions.
  - Returns sorted absolute paths.

- `_ensure_screen()`
  - Initializes pygame and opens fullscreen display.

- `_ensure_screen_safe()`
  - Safe wrapper for screen init.
  - Logs error and returns `(None, None)` on failure.

- `_scale_image(img, screen_size)`
  - Resizes image preserving aspect ratio.
  - Adds black background to fill screen.

- `_play_image(path, screen, screen_size)`
  - Renders photo with pygame.
  - Shows for configured interval.
  - Handles pending delete and file removal during display.
  - Returns:
    - `None` on ESC key exit.
    - `True` on success.
    - fallback result when pygame fails.

- `_play_image_fallback(path)`
  - Uses ffplay loop mode for images.
  - Stops process at interval end.
  - Faster poll loop for reduced transition lag.

- `_play_video(path)`
  - Closes pygame display, plays video with ffplay.
  - Terminates on pending delete or missing file.

- `run_slideshow()`
  - Infinite main loop:
    - Collects media list.
    - Skips pending/missing files.
    - Plays photo/video based on extension.
    - Handles idle state when no media exists.

---

### File: `media_controller/templates/index.html`
Purpose:
- Frontend UI template for media control dashboard.

Main sections:
- Hero header with status (`RUNNING` / `STOPPED`).
- Start/Stop control buttons.
- Playback interval form.
- File upload form.
- Media library listing with delete buttons.

Template data required:
- `config`
- `running`
- `photos`
- `videos`

---

### File: `install_shop_service.sh`
Purpose:
- One-command Raspberry Pi production setup for shops.

Function:
- `install_system_packages()`
  - Installs system dependencies: ffmpeg, SDL libs, python3-venv.

Main step flow:
1. Check `python3`.
2. Install packages (if needed).
3. Create `.venv`.
4. Install Python requirements.
5. Create runtime files/folders (`photos/`, `videos/`, `config.json`, `pending_delete.json`).
6. Disable old conflicting services.
7. Write `/etc/systemd/system/media-controller.service`.
8. Enable and start service.

---

### File: `README_RASPBERRY_PI.md`
Purpose:
- Human-readable deployment and operational guide.

Contains:
- Scalable structure overview.
- One-time setup commands.
- Daily operation steps.
- Service and log commands.
- VM networking guidance.

---

### File: `requirements.txt`
Purpose:
- Python dependency versions.

Dependencies:
- `Flask>=3.0,<4`
- `Werkzeug>=3.0,<4`
- `pygame>=2.5,<3`

---

### File: `config.json`
Purpose:
- Runtime configuration storage.

Current schema:
- `photo_interval` (integer seconds, min value enforced as 1 in backend).

---

### File: `pending_delete.json`
Purpose:
- Stores list of absolute normalized file paths pending deletion.

Schema:
- JSON array of strings.

---

### File: `.gitignore`
Purpose:
- Keeps runtime artifacts and local files out of source control.

Ignored:
- Python cache files.
- `.log`, `.pid`, `.tmp`.
- `.venv/`.

## 5) Endpoint Reference

- `GET /`
  - Dashboard page.

- `POST /start`
  - Starts slideshow process.

- `POST /stop`
  - Stops slideshow process.

- `POST /upload`
  - Upload image/video.

- `POST /set_interval`
  - Update photo interval.

- `POST /delete/<media_type>/<filename>`
  - Delete selected media file safely.

## 6) Important Runtime Files

- `slideshow.pid`
  - Active slideshow PID.
- `slideshow.out.log`
  - Slideshow stdout log.
- `slideshow.err.log`
  - Slideshow stderr log.
- `slideshow.log`
  - Internal playback engine log.

## 7) Operational Notes

- For phone access, open `http://<device-ip>:5000`.
- If running inside VM:
  - Use Bridged mode.
  - NAT IP (example `10.0.2.x`) may not be reachable from phone.
- Some Raspberry Pi hardware may show small transition delay between media types.

## 8) Quick Maintenance Commands

```bash
sudo systemctl status media-controller.service
sudo systemctl restart media-controller.service
sudo systemctl stop media-controller.service
sudo journalctl -u media-controller.service -n 100 --no-pager
tail -n 100 slideshow.err.log
tail -n 100 slideshow.out.log
tail -n 100 slideshow.log
```
