import json
from pathlib import Path


def test_read_status_file(tmp_path):
    from watchingai.status import StatusReader
    status_file = tmp_path / "status.json"
    status_file.write_text(json.dumps({
        "status": "working",
        "detail": "src/main.py 편집 중",
        "timestamp": "2026-04-21T19:30:00",
        "elapsed_seconds": 12,
    }))

    reader = StatusReader(status_dir=tmp_path)
    status = reader.read()
    assert status.state == "working"
    assert status.detail == "src/main.py 편집 중"
    assert status.elapsed_seconds == 12


def test_missing_status_file_returns_idle(tmp_path):
    from watchingai.status import StatusReader
    reader = StatusReader(status_dir=tmp_path)
    status = reader.read()
    assert status.state == "idle"
    assert status.detail == ""


def test_stale_timestamp_returns_idle(tmp_path):
    from watchingai.status import StatusReader
    status_file = tmp_path / "status.json"
    status_file.write_text(json.dumps({
        "status": "working",
        "detail": "something",
        "timestamp": "2020-01-01T00:00:00",
        "elapsed_seconds": 5,
    }))

    reader = StatusReader(status_dir=tmp_path, stale_seconds=30)
    status = reader.read()
    assert status.state == "idle"


def test_corrupt_status_file_returns_idle(tmp_path):
    from watchingai.status import StatusReader
    status_file = tmp_path / "status.json"
    status_file.write_text("broken json {{{")

    reader = StatusReader(status_dir=tmp_path)
    status = reader.read()
    assert status.state == "idle"


def test_status_equality():
    from watchingai.status import Status
    s1 = Status(state="working", detail="editing", elapsed_seconds=5)
    s2 = Status(state="working", detail="editing", elapsed_seconds=5)
    s3 = Status(state="idle", detail="", elapsed_seconds=0)
    assert s1 == s2
    assert s1 != s3
