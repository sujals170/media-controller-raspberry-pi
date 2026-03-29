# Media Controller for Raspberry Pi

Smart media display app for Raspberry Pi shops. Show photos and videos on a TV screen and control playback from a simple web panel.

## Platform Support

- Windows: App runs normally (Flask web panel + playback logic)
- Raspberry Pi/Linux: Full support including auto-start service setup
- `install_shop_service.sh` and `systemd` commands are Linux/Raspberry Pi only

## Features

- Web control panel for starting and managing playback
- Slideshow support for photos and videos
- Service-based startup on boot (`systemd`)
- Folder-based media management (`photos/` and `videos/`)
- Lightweight Flask backend

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

## Quick Start on Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://localhost:5000
```

## Quick Start on Linux/Raspberry Pi

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://<device-ip>:5000
```

## Raspberry Pi Service Setup

```bash
chmod +x install_shop_service.sh
bash install_shop_service.sh
```

After installation, useful commands:

```bash
sudo systemctl status media-controller.service
sudo systemctl restart media-controller.service
sudo journalctl -u media-controller.service -n 100 --no-pager
```

## Notes

- Keep Raspberry Pi and phone/PC on same network for web access.
- Use a stable LAN IP for reliable shop usage.
