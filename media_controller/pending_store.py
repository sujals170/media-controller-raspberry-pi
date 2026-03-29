import json
import os
import tempfile

from werkzeug.utils import secure_filename

from .constants import (
    PENDING_DELETE_FILE,
    PHOTO_FOLDER,
    PROJECT_ROOT,
    VIDEO_FOLDER,
)


def norm_path(path):
    return os.path.normcase(os.path.abspath(path))


def load_pending():
    try:
        with open(PENDING_DELETE_FILE, encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, list):
            return set(data)
    except Exception:
        pass
    return set()


def save_pending(pending):
    tmp = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        delete=False,
        dir=PROJECT_ROOT,
        suffix=".pending.tmp",
    )
    tmp_path = tmp.name
    tmp.close()
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(sorted(pending), handle)
    os.replace(tmp_path, PENDING_DELETE_FILE)


def add_pending(path):
    pending = load_pending()
    pending.add(norm_path(path))
    save_pending(pending)


def remove_pending(path):
    pending = load_pending()
    pending.discard(norm_path(path))
    save_pending(pending)


def is_pending(path):
    return norm_path(path) in load_pending()


def try_clear_pending(path):
    pending = load_pending()
    normalized = norm_path(path)
    if normalized not in pending:
        return

    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            return

    pending.discard(normalized)
    save_pending(pending)


def is_within(base_folder, path):
    base = norm_path(base_folder)
    target = norm_path(path)
    return os.path.commonpath([base, target]) == base


def resolve_media_path(media_type, filename):
    folder = PHOTO_FOLDER if media_type == "photo" else VIDEO_FOLDER
    safe_name = secure_filename(filename)
    full_path = os.path.abspath(os.path.join(folder, safe_name))
    if not is_within(folder, full_path):
        return None
    return full_path
