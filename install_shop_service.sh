#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
REQ_FILE="$PROJECT_DIR/requirements.txt"
SERVICE_NAME="media-controller.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
RUN_USER="${SUDO_USER:-$USER}"

install_system_packages() {
  if command -v sudo >/dev/null 2>&1; then
    sudo apt update
    sudo apt install -y ffmpeg libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 python3-venv
  else
    apt update
    apt install -y ffmpeg libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0 python3-venv
  fi
}

echo "[1/8] Checking python3..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Install Python3 first."
  exit 1
fi

echo "[2/8] Installing system packages..."
if ! command -v ffplay >/dev/null 2>&1; then
  install_system_packages
fi

echo "[3/8] Creating virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "[4/8] Installing Python dependencies..."
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip
pip install -r "$REQ_FILE"
deactivate

echo "[5/8] Creating runtime folders/files..."
mkdir -p "$PROJECT_DIR/photos" "$PROJECT_DIR/videos"
[ -f "$PROJECT_DIR/config.json" ] || printf '{"photo_interval": 5}\n' > "$PROJECT_DIR/config.json"
[ -f "$PROJECT_DIR/pending_delete.json" ] || printf '[]\n' > "$PROJECT_DIR/pending_delete.json"

echo "[6/8] Disabling old conflicting services (if present)..."
for old_service in web-slideshow.service slideshow.service; do
  if systemctl list-unit-files | grep -q "^${old_service}"; then
    sudo systemctl stop "$old_service" || true
    sudo systemctl disable "$old_service" || true
  fi
done

echo "[7/8] Writing systemd service..."
sudo tee "$SERVICE_PATH" >/dev/null <<EOF
[Unit]
Description=Media Controller Flask App
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$PROJECT_DIR
Environment=PYTHONUNBUFFERED=1
Environment=DISPLAY=:0
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "[8/8] Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable --now "$SERVICE_NAME"

IP_ADDR="$(hostname -I | awk '{print $1}')"
echo
echo "Setup complete."
echo "Service status:"
sudo systemctl --no-pager --full status "$SERVICE_NAME" | sed -n '1,12p'
echo
echo "Open on phone/browser:"
echo "http://$IP_ADDR:5000"
