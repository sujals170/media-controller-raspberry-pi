import os
import signal
import subprocess
import tempfile
import time

from .constants import PROJECT_ROOT, SLIDESHOW_PID_FILE


def write_pid(pid):
    tmp = tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        delete=False,
        dir=PROJECT_ROOT,
        suffix=".pid.tmp",
    )
    tmp_path = tmp.name
    tmp.close()
    with open(tmp_path, "w", encoding="utf-8") as handle:
        handle.write(str(pid))
    os.replace(tmp_path, SLIDESHOW_PID_FILE)


def read_pid():
    if not os.path.exists(SLIDESHOW_PID_FILE):
        return None
    try:
        with open(SLIDESHOW_PID_FILE, encoding="utf-8") as handle:
            return int(handle.read().strip())
    except Exception:
        return None


def clear_pid():
    try:
        if os.path.exists(SLIDESHOW_PID_FILE):
            os.remove(SLIDESHOW_PID_FILE)
    except Exception:
        pass


def pid_exists(pid):
    if pid is None or pid <= 0:
        return False
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
            )
            return str(pid) in result.stdout
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def kill_pid(pid):
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
            return

        try:
            # On POSIX, stop the whole process group so ffplay child processes die too.
            os.killpg(pid, signal.SIGTERM)
            time.sleep(0.4)
            if pid_exists(pid):
                os.killpg(pid, signal.SIGKILL)
        except Exception:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.2)
            if pid_exists(pid):
                os.kill(pid, signal.SIGKILL)
    except Exception:
        pass


def is_running(local_process=None):
    if local_process is not None and local_process.poll() is None:
        return True
    pid = read_pid()
    running = pid is not None and pid_exists(pid)
    if pid is not None and not running:
        clear_pid()
    return running
