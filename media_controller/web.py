import os
import subprocess
import sys
import time

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from .config_store import get_config, save_config
from .constants import (
    ALLOWED_PHOTO_EXTS,
    ALLOWED_VIDEO_EXTS,
    PHOTO_FOLDER,
    PROJECT_ROOT,
    SLIDESHOW_ERR_LOG_FILE,
    SLIDESHOW_OUT_LOG_FILE,
    VIDEO_FOLDER,
    ensure_runtime_dirs,
)
from .networking import get_lan_ip
from .pending_store import add_pending, remove_pending, resolve_media_path
from .process_manager import (
    clear_pid,
    is_running,
    kill_pid,
    pid_exists,
    read_pid,
    write_pid,
)


def _slideshow_env():
    env = os.environ.copy()
    if os.name != "nt" and not env.get("DISPLAY"):
        env["DISPLAY"] = ":0"
    return env


def create_app():
    ensure_runtime_dirs()
    app = Flask(__name__, template_folder="templates")
    state = {"slideshow_process": None}

    @app.route("/")
    def index():
        photos = [
            name
            for name in os.listdir(PHOTO_FOLDER)
            if os.path.splitext(name)[1].lower() in ALLOWED_PHOTO_EXTS
        ]
        videos = [
            name
            for name in os.listdir(VIDEO_FOLDER)
            if os.path.splitext(name)[1].lower() in ALLOWED_VIDEO_EXTS
        ]
        return render_template(
            "index.html",
            config=get_config(),
            running=is_running(state["slideshow_process"]),
            photos=sorted(photos),
            videos=sorted(videos),
        )

    @app.route("/start", methods=["POST"])
    def start_slideshow():
        pid = read_pid()
        if pid is not None and pid_exists(pid):
            return redirect(url_for("index"))

        process = state["slideshow_process"]
        if process is None or process.poll() is not None:
            script_path = os.path.join(PROJECT_ROOT, "slideshow.py")
            kwargs = {"cwd": PROJECT_ROOT, "env": _slideshow_env()}
            if os.name != "nt":
                kwargs["start_new_session"] = True

            with open(SLIDESHOW_OUT_LOG_FILE, "a", encoding="utf-8") as out_log, open(
                SLIDESHOW_ERR_LOG_FILE, "a", encoding="utf-8"
            ) as err_log:
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=out_log,
                    stderr=err_log,
                    **kwargs,
                )

            state["slideshow_process"] = process
            write_pid(process.pid)
            time.sleep(0.2)
            if process.poll() is not None:
                clear_pid()

        return redirect(url_for("index"))

    @app.route("/stop", methods=["POST"])
    def stop_slideshow():
        process = state["slideshow_process"]
        if process and process.poll() is None:
            kill_pid(process.pid)
            state["slideshow_process"] = None

        pid = read_pid()
        if pid is not None:
            kill_pid(pid)
        clear_pid()
        return redirect(url_for("index"))

    @app.route("/upload", methods=["POST"])
    def upload_file():
        file = request.files.get("file")
        if file and file.filename:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in ALLOWED_PHOTO_EXTS:
                folder = PHOTO_FOLDER
            elif ext in ALLOWED_VIDEO_EXTS:
                folder = VIDEO_FOLDER
            else:
                return redirect(url_for("index"))

            saved_path = os.path.join(folder, filename)
            file.save(saved_path)
            remove_pending(saved_path)
        return redirect(url_for("index"))

    @app.route("/set_interval", methods=["POST"])
    def set_interval():
        config = get_config()
        try:
            interval = int(request.form.get("interval", config.get("photo_interval", 5)))
        except (TypeError, ValueError):
            interval = config.get("photo_interval", 5)
        config["photo_interval"] = max(1, interval)
        save_config(config)
        return redirect(url_for("index"))

    @app.route("/delete/<media_type>/<filename>", methods=["POST"])
    def delete_file(media_type, filename):
        if media_type not in {"photo", "video"}:
            return redirect(url_for("index"))

        path = resolve_media_path(media_type, filename)
        if path is None:
            return redirect(url_for("index"))

        if os.path.exists(path):
            try:
                os.remove(path)
                remove_pending(path)
            except Exception:
                add_pending(path)
        else:
            remove_pending(path)
        return redirect(url_for("index"))

    return app


def run():
    app = create_app()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    if host == "0.0.0.0":
        print(f"Open from phone on same Wi-Fi: http://{get_lan_ip()}:{port}")
    app.run(host=host, port=port)
