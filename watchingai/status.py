import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Status:
    state: str
    detail: str
    elapsed_seconds: int

    def __eq__(self, other):
        if not isinstance(other, Status):
            return False
        return (self.state == other.state
                and self.detail == other.detail
                and self.elapsed_seconds == other.elapsed_seconds)


IDLE = Status(state="idle", detail="", elapsed_seconds=0)


class StatusReader:
    def __init__(self, status_dir: Path | None = None, stale_seconds: int = 30):
        if status_dir is None:
            status_dir = Path.home() / ".watchingai"
        self._status_file = status_dir / "status.json"
        self._stale_seconds = stale_seconds

    def read(self) -> Status:
        if not self._status_file.exists():
            return IDLE

        try:
            with open(self._status_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return IDLE

        timestamp_str = data.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(timestamp_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if (now - ts).total_seconds() > self._stale_seconds:
                return IDLE
        except ValueError:
            return IDLE

        return Status(
            state=data.get("status", "idle"),
            detail=data.get("detail", ""),
            elapsed_seconds=data.get("elapsed_seconds", 0),
        )
