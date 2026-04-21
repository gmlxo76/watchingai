#!/usr/bin/env python3
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WATCHINGAI_DIR = Path.home() / ".watchingai"
STATUS_FILE = WATCHINGAI_DIR / "status.json"
WATCHINGAI_DIR.mkdir(parents=True, exist_ok=True)

hook_input = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}

event = hook_input.get("hook_event_name", "")
tool_name = hook_input.get("tool_name", "")
tool_input = hook_input.get("tool_input", {})
if isinstance(tool_input, str):
    try:
        tool_input = json.loads(tool_input)
    except (json.JSONDecodeError, TypeError):
        tool_input = {}

timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def write_status(status: str, detail: str):
    data = {
        "status": status,
        "detail": detail,
        "timestamp": timestamp,
        "elapsed_seconds": 0,
    }
    STATUS_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


if event == "SessionStart":
    write_status("idle", "")
elif event == "UserPromptSubmit":
    write_status("thinking", "요청 처리 중...")
elif event == "PreToolUse":
    if tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path", "unknown") if isinstance(tool_input, dict) else "unknown"
        write_status("working", f"{Path(file_path).name} 편집 중")
    elif tool_name in ("Bash", "PowerShell"):
        cmd = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
        write_status("working", f"명령 실행: {cmd[:50]}")
    elif tool_name in ("Read", "Glob", "Grep"):
        write_status("working", "파일 탐색 중")
    else:
        write_status("working", f"{tool_name} 실행 중")
elif event == "PostToolUse":
    write_status("done", "완료")
elif event == "PostToolUseFailure":
    write_status("error", f"{tool_name} 실패")
elif event in ("Stop", "SessionEnd"):
    write_status("idle", "")
