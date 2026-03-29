# Media Controller for Raspberry Pi

Smart media display app for shops.  
You can show photos/videos on a TV screen and control playback from a simple web panel.

## Where It Works

- Windows laptop/desktop: Supported for normal app usage
- Linux/Raspberry Pi: Fully supported (including auto-start service)
- `install_shop_service.sh`: Linux/Raspberry Pi only

## What You Need Before Setup

- Python 3.9+ installed
- Internet for first-time dependency install
- This project folder downloaded/cloned on your system

## Fast Setup for Windows Users

Open PowerShell in project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open in browser:

```text
http://localhost:5000
```

## Fast Setup for Linux/Raspberry Pi Users

### Option A: Manual run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open in browser:

```text
http://<device-ip>:5000
```

### Option B: Auto-start service (recommended for shop use)

```bash
chmod +x install_shop_service.sh
bash install_shop_service.sh
```

This script installs required packages, creates `.venv`, sets up `media-controller.service`, and starts it.

## How to Use After Setup

- Put images in `photos/`
- Put videos in `videos/`
- Start app/service
- Open web panel and control playback

## Useful Commands (Raspberry Pi)

```bash
sudo systemctl status media-controller.service
sudo systemctl restart media-controller.service
sudo systemctl stop media-controller.service
sudo journalctl -u media-controller.service -n 100 --no-pager
```

## Troubleshooting

- `python` not found: install Python and reopen terminal
- `pip install` fails: check internet and rerun command
- Port `5000` already in use: stop old process or run on another port
- Phone cannot open panel: keep phone and device on same Wi-Fi/LAN

## Project Structure

```text
Py/
  app.py
  slideshow.py
  install_shop_service.sh
  media_controller/
    web.py
    slideshow_runner.py
    process_manager.py
    networking.py
    templates/index.html
  photos/
  videos/
  config.json
  pending_delete.json
```
