# Raspberry Pi Shop Setup

Use this when delivering to a shop so app auto-starts after reboot.

## Scalable Project Structure

```text
Py/
  app.py                      # web entrypoint
  slideshow.py                # slideshow entrypoint
  install_shop_service.sh
  media_controller/
    __init__.py
    constants.py
    config_store.py
    pending_store.py
    process_manager.py
    networking.py
    web.py                    # Flask routes and lifecycle
    slideshow_runner.py       # playback engine
    templates/
      index.html              # UI template
  photos/
  videos/
  config.json
  pending_delete.json
```

## One-Time Setup on Raspberry Pi

```bash
cd /path/to/this-folder
chmod +x install_shop_service.sh
bash install_shop_service.sh
```

This will:
- install required system packages
- create `.venv` and install Python packages
- create needed folders/files
- stop old `web-slideshow.service` and `slideshow.service` if present
- install and start `media-controller.service`
- enable auto-start at boot

After setup, open:

```text
http://<raspberry-pi-ip>:5000
```

## Daily Use for Shop Owner

- Power on Raspberry Pi.
- Open phone/PC browser on same Wi-Fi.
- Visit `http://<raspberry-pi-ip>:5000`.
- Press `START` from web page when needed.

## Useful Service Commands

```bash
sudo systemctl status media-controller.service
sudo systemctl restart media-controller.service
sudo systemctl stop media-controller.service
sudo journalctl -u media-controller.service -n 100 --no-pager
tail -n 100 slideshow.err.log
tail -n 100 slideshow.out.log
```

## If Running Inside a VM

- VM must be in `Bridged` mode, not NAT.
- If VM IP looks like `10.0.2.x`, phone usually cannot reach it.
- Use bridged LAN IP (for example `192.168.x.x`).
