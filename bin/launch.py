import hashlib
import os
import platform
import subprocess
import sys
from pathlib import Path

WATCHINGAI_DIR = Path.home() / ".watchingai"
WATCHINGAI_DIR.mkdir(parents=True, exist_ok=True)

def get_project_id():
    if platform.system() == "Windows":
        result = subprocess.run(
            ["bash", "-c", "echo $PWD"],
            capture_output=True, text=True,
        )
        cwd = result.stdout.strip() + "\n"
    else:
        cwd = os.getcwd() + "\n"
    return hashlib.md5(cwd.encode()).hexdigest()[:8]

project_id = sys.argv[1] if len(sys.argv) > 1 else get_project_id()

pid_file = WATCHINGAI_DIR / f"pid_{project_id}.txt"
if pid_file.exists():
    old_pid = pid_file.read_text().strip()
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {old_pid}"],
                capture_output=True, text=True,
            )
            if old_pid in result.stdout:
                sys.exit(0)
        else:
            os.kill(int(old_pid), 0)
            sys.exit(0)
    except (OSError, ValueError):
        pid_file.unlink(missing_ok=True)

try:
    __import__("watchingai")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "watchingai"])

(WATCHINGAI_DIR / f"project_{project_id}.path").write_text(os.getcwd(), encoding="utf-8")

args = [sys.executable, "-m", "watchingai", "--project-id", project_id]
kwargs = dict(
    close_fds=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
if platform.system() == "Windows":
    kwargs["creationflags"] = 0x00000008
else:
    kwargs["start_new_session"] = True

subprocess.Popen(args, **kwargs)

lock_file = WATCHINGAI_DIR / f"lock_{project_id}"
lock_file.touch()
