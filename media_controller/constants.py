import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO_FOLDER = os.path.join(PROJECT_ROOT, "photos")
VIDEO_FOLDER = os.path.join(PROJECT_ROOT, "videos")
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")
PENDING_DELETE_FILE = os.path.join(PROJECT_ROOT, "pending_delete.json")
SLIDESHOW_PID_FILE = os.path.join(PROJECT_ROOT, "slideshow.pid")
SLIDESHOW_OUT_LOG_FILE = os.path.join(PROJECT_ROOT, "slideshow.out.log")
SLIDESHOW_ERR_LOG_FILE = os.path.join(PROJECT_ROOT, "slideshow.err.log")
SLIDESHOW_LOG_FILE = os.path.join(PROJECT_ROOT, "slideshow.log")

ALLOWED_PHOTO_EXTS = {".png", ".jpg", ".jpeg"}
ALLOWED_VIDEO_EXTS = {".mp4", ".mov", ".avi"}


def ensure_runtime_dirs():
    for folder in (PHOTO_FOLDER, VIDEO_FOLDER):
        os.makedirs(folder, exist_ok=True)
