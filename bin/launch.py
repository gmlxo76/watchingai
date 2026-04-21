import subprocess
import sys
import platform

project_id = sys.argv[1] if len(sys.argv) > 1 else None
args = [sys.executable, "-m", "watchingai"]
if project_id:
    args += ["--project-id", project_id]

kwargs = dict(
    close_fds=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
if platform.system() == "Windows":
    kwargs["creationflags"] = 0x00000008

subprocess.Popen(args, **kwargs)
