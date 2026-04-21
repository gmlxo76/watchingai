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
    ACTIVE_STATES = {"thinking", "working", "done"}

    def __init__(self, status_dir: Path | None = None, stale_seconds: int = 30,
                 project_id: str | None = None):
        if status_dir is None:
            status_dir = Path.home() / ".watchingai"
        self._status_dir = status_dir
        self._stale_seconds = stale_seconds
        self._project_id = project_id

    def _read_file(self, path: Path) -> tuple[Status, datetime | None]:
        if not path.exists():
            return IDLE, None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return IDLE, None

        state = data.get("status", "idle")
        timestamp_str = data.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(timestamp_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            if state not in self.ACTIVE_STATES and (now - ts).total_seconds() > self._stale_seconds:
                return IDLE, ts
        except ValueError:
            return IDLE, None

        status = Status(
            state=state,
            detail=data.get("detail", ""),
            elapsed_seconds=data.get("elapsed_seconds", 0),
        )
        return status, ts

    def read(self) -> Status:
        if self._project_id:
            target = self._status_dir / f"status_{self._project_id}.json"
            s, _ = self._read_file(target)
            return s

        best_status = IDLE
        best_ts = None

        old_file = self._status_dir / "status.json"
        s, t = self._read_file(old_file)
        if t and (best_ts is None or t > best_ts):
            best_status, best_ts = s, t

        if self._status_dir.exists():
            for f in self._status_dir.glob("status_*.json"):
                s, t = self._read_file(f)
                if t and (best_ts is None or t > best_ts):
                    best_status, best_ts = s, t

        return best_status
