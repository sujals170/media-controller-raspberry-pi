import glob
import os
import subprocess
import time
from datetime import datetime

import pygame

from .config_store import get_config
from .constants import (
    ALLOWED_PHOTO_EXTS,
    ALLOWED_VIDEO_EXTS,
    PHOTO_FOLDER,
    SLIDESHOW_LOG_FILE,
    VIDEO_FOLDER,
)
from .pending_store import is_pending, try_clear_pending

FFPLAY_IMAGE_COMMON = [
    "ffplay",
    "-fs",
    "-autoexit",
    "-loglevel",
    "quiet",
]

FFPLAY_VIDEO_COMMON = [
    "ffplay",
    "-fs",
    "-autoexit",
    "-loglevel",
    "quiet",
    "-an",
    "-fflags",
    "nobuffer",
    "-flags",
    "low_delay",
    "-probesize",
    "32",
    "-analyzeduration",
    "0",
]


def get_interval():
    try:
        return max(1, int(get_config().get("photo_interval", 5)))
    except Exception:
        return 5


def _log(msg):
    try:
        line = f"{datetime.now().isoformat(timespec='seconds')} {msg}\n"
        with open(SLIDESHOW_LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write(line)
    except Exception:
        pass


def _list_media():
    photos = glob.glob(os.path.join(PHOTO_FOLDER, "*.*"))
    videos = glob.glob(os.path.join(VIDEO_FOLDER, "*.*"))
    media = []
    for fpath in photos + videos:
        ext = os.path.splitext(fpath)[1].lower()
        if ext in ALLOWED_PHOTO_EXTS or ext in ALLOWED_VIDEO_EXTS:
            media.append(os.path.abspath(fpath))
    return sorted(media, key=lambda path: os.path.basename(path).lower())


def _ensure_screen():
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()
    pygame.mouse.set_visible(False)
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    return screen, (info.current_w, info.current_h)


def _ensure_screen_safe():
    try:
        return _ensure_screen()
    except Exception as err:
        _log(f"screen init failed, using ffplay-only mode: {err}")
        return None, None


def _scale_image(img, screen_size):
    rect = img.get_rect()
    scale = min(screen_size[0] / rect.width, screen_size[1] / rect.height)
    new_size = (int(rect.width * scale), int(rect.height * scale))
    scaled = pygame.transform.smoothscale(img, new_size)
    surface = pygame.Surface(screen_size)
    surface.fill((0, 0, 0))
    pos = ((screen_size[0] - new_size[0]) // 2, (screen_size[1] - new_size[1]) // 2)
    surface.blit(scaled, pos)
    return surface


def _play_image(path, screen, screen_size):
    if screen is None or screen_size is None:
        screen, screen_size = _ensure_screen_safe()
        if screen is None or screen_size is None:
            return _play_image_fallback(path)

    if not pygame.display.get_init():
        screen, screen_size = _ensure_screen_safe()
        if screen is None or screen_size is None:
            return _play_image_fallback(path)

    try:
        img = pygame.image.load(path).convert()
        frame = _scale_image(img, screen_size)
        screen.blit(frame, (0, 0))
        pygame.display.flip()
    except Exception as err:
        _log(f"pygame image render failed for {path}: {err}")
        return _play_image_fallback(path)

    start = time.monotonic()
    while time.monotonic() - start < get_interval():
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
        if is_pending(path):
            try_clear_pending(path)
            break
        if not os.path.exists(path):
            break
        time.sleep(0.1)
    return True


def _play_image_fallback(path):
    proc = None
    try:
        proc = subprocess.Popen(
            FFPLAY_IMAGE_COMMON + ["-f", "image2", "-loop", "1", path],
            shell=False,
        )
        interval_reached = False
        start = time.monotonic()
        while time.monotonic() - start < get_interval():
            if is_pending(path) or not os.path.exists(path):
                proc.terminate()
                break
            if proc.poll() is not None:
                break
            time.sleep(0.03)
        else:
            interval_reached = True

        if interval_reached and proc.poll() is None:
            proc.terminate()
        return True
    except Exception as err:
        _log(f"ffplay image fallback failed for {path}: {err}")
        return False
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.wait(timeout=0.25)
            except Exception:
                proc.kill()


def _play_video(path):
    proc = None
    try:
        if pygame.display.get_init():
            pygame.display.quit()
        proc = subprocess.Popen(FFPLAY_VIDEO_COMMON + [path], shell=False)
        while proc.poll() is None:
            if is_pending(path) or not os.path.exists(path):
                proc.terminate()
                break
            time.sleep(0.03)
    except Exception as err:
        _log(f"video playback failed for {path}: {err}")
    finally:
        if proc is not None and proc.poll() is None:
            try:
                proc.wait(timeout=0.25)
            except Exception:
                proc.kill()
        if is_pending(path):
            try_clear_pending(path)


def run_slideshow():
    screen, screen_size = _ensure_screen_safe()
    last_path = None

    while True:
        media = [path for path in _list_media() if not is_pending(path)]
        if not media:
            if screen is not None and pygame.display.get_init():
                screen.fill((20, 20, 20))
                pygame.display.flip()
                pygame.event.pump()
            time.sleep(1)
            continue

        next_index = (media.index(last_path) + 1) % len(media) if last_path in media else 0
        path = media[next_index]
        last_path = path

        if is_pending(path):
            try_clear_pending(path)
            continue
        if not os.path.exists(path):
            continue

        ext = os.path.splitext(path)[1].lower()
        if ext in ALLOWED_PHOTO_EXTS:
            if screen is None or screen_size is None or not pygame.display.get_init():
                screen, screen_size = _ensure_screen_safe()
            result = _play_image(path, screen, screen_size)
            if result is None:
                return
            if result is False:
                _log(f"image skipped after both render methods failed: {path}")
            continue

        if ext in ALLOWED_VIDEO_EXTS:
            _play_video(path)
            screen, screen_size = None, None
