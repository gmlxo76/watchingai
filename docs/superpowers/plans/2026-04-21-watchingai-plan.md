# WatchingAI 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Claude Code의 작업 상태를 데스크톱 위에 스프라이트 캐릭터로 표시하는 플러그인 + 데스크톱 앱을 만든다.

**Architecture:** Claude Code 플러그인이 hooks를 통해 상태를 `~/.watchingai/status.json`에 기록하고, PyQt 데스크톱 앱이 해당 파일을 폴링하여 투명 창 위에 스프라이트 애니메이션을 렌더링한다.

**Tech Stack:** Python 3, PyQt6, PyInstaller, Claude Code Plugin (bash hooks)

---

## 파일 구조

```
WatchingAI/
├── .claude-plugin/
│   └── plugin.json                # 플러그인 메타정보
├── hooks/
│   └── hooks.json                 # hooks 설정
├── bin/
│   └── watchingai-status.sh       # 상태 기록 스크립트
├── setup.sh                       # 데스크톱 앱 자동 설치
├── watchingai/                    # Python 패키지
│   ├── __init__.py
│   ├── __main__.py                # 진입점
│   ├── config.py                  # 설정 로드/저장
│   ├── status.py                  # 상태 파일 폴링
│   ├── sprite.py                  # 스프라이트 시트 로드/프레임 추출
│   ├── widget.py                  # 투명 위젯 창 + 애니메이션
│   └── tray.py                    # 시스템 트레이 메뉴
├── assets/
│   └── default_sprite.png         # 디폴트 스프라이트 시트
├── tests/
│   ├── test_config.py
│   ├── test_status.py
│   ├── test_sprite.py
│   └── test_widget.py
├── pyproject.toml                 # 패키지 설정
└── README.md
```

---

### Task 1: 프로젝트 초기화 및 패키지 설정

**Files:**
- Create: `pyproject.toml`
- Create: `watchingai/__init__.py`
- Create: `watchingai/__main__.py`

- [ ] **Step 1: pyproject.toml 생성**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "watchingai"
version = "0.1.0"
description = "Desktop sprite widget that shows Claude Code's working status"
requires-python = ">=3.9"
dependencies = [
    "PyQt6>=6.5.0",
]

[project.scripts]
watchingai = "watchingai.__main__:main"

[tool.setuptools.packages.find]
include = ["watchingai*"]

[tool.setuptools.package-data]
watchingai = ["../assets/*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: __init__.py 생성**

```python
__version__ = "0.1.0"
```

- [ ] **Step 3: __main__.py 생성**

```python
import sys

def main():
    print("WatchingAI starting...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 가상환경 생성 및 의존성 설치**

Run: `python -m venv .venv && .venv/Scripts/activate && pip install -e ".[dev]" PyQt6 pytest`
Expected: 성공적으로 설치 완료

- [ ] **Step 5: 실행 확인**

Run: `python -m watchingai`
Expected: "WatchingAI starting..." 출력

- [ ] **Step 6: 커밋**

```bash
git init
git add pyproject.toml watchingai/__init__.py watchingai/__main__.py
git commit -m "feat: 프로젝트 초기화 및 패키지 설정"
```

---

### Task 2: 설정 모듈 (config.py)

**Files:**
- Create: `watchingai/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_config.py
import json
import os
from pathlib import Path

def test_default_config_created(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    assert config.position_preset == "bottom-right"
    assert config.sprite_sheet == "default_sprite.png"
    assert config.frame_width == 64
    assert config.frame_height == 64
    assert config.size == 64
    assert config.poll_interval_ms == 1500
    assert "idle" in config.animations
    assert "working" in config.animations
    assert "thinking" in config.animations
    assert "done" in config.animations
    assert "error" in config.animations

def test_config_saves_and_loads(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    config.position_preset = "top-left"
    config.size = 128
    config.save()

    config2 = Config(config_dir=tmp_path)
    assert config2.position_preset == "top-left"
    assert config2.size == 128

def test_config_custom_position(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    config.custom_position = (100, 200)
    config.save()

    config2 = Config(config_dir=tmp_path)
    assert config2.custom_position == (100, 200)

def test_config_animation_mapping(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    config.animations["idle"] = {"row": 9, "columns": [1, 2, 3, 4]}
    config.save()

    config2 = Config(config_dir=tmp_path)
    assert config2.animations["idle"]["row"] == 9
    assert config2.animations["idle"]["columns"] == [1, 2, 3, 4]

def test_config_corrupt_file_resets_to_default(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("not valid json{{{")

    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    assert config.position_preset == "bottom-right"
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL — `No module named 'watchingai.config'`

- [ ] **Step 3: config.py 구현**

```python
# watchingai/config.py
import json
from pathlib import Path

DEFAULT_ANIMATIONS = {
    "idle": {"row": 1, "columns": [1, 2, 3]},
    "thinking": {"row": 3, "columns": [1, 2]},
    "working": {"row": 4, "columns": [1, 2, 3, 4]},
    "done": {"row": 6, "columns": [2, 4]},
    "error": {"row": 8, "columns": [1, 2, 3]},
}

DEFAULT_CONFIG = {
    "position": {
        "preset": "bottom-right",
        "custom": None,
    },
    "sprite": {
        "sheet": "default_sprite.png",
        "frame_width": 64,
        "frame_height": 64,
        "animations": DEFAULT_ANIMATIONS,
    },
    "size": 64,
    "poll_interval_ms": 1500,
}


class Config:
    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            config_dir = Path.home() / ".watchingai"
        self._config_dir = config_dir
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self._config_dir / "config.json"
        self._data = self._load()

    def _load(self) -> dict:
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        data = json.loads(json.dumps(DEFAULT_CONFIG))
        self._save_data(data)
        return data

    def _save_data(self, data: dict) -> None:
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self) -> None:
        self._save_data(self._data)

    @property
    def position_preset(self) -> str:
        return self._data["position"]["preset"]

    @position_preset.setter
    def position_preset(self, value: str) -> None:
        self._data["position"]["preset"] = value

    @property
    def custom_position(self) -> tuple[int, int] | None:
        val = self._data["position"]["custom"]
        if val is not None:
            return tuple(val)
        return None

    @custom_position.setter
    def custom_position(self, value: tuple[int, int] | None) -> None:
        self._data["position"]["custom"] = list(value) if value else None

    @property
    def sprite_sheet(self) -> str:
        return self._data["sprite"]["sheet"]

    @sprite_sheet.setter
    def sprite_sheet(self, value: str) -> None:
        self._data["sprite"]["sheet"] = value

    @property
    def frame_width(self) -> int:
        return self._data["sprite"]["frame_width"]

    @property
    def frame_height(self) -> int:
        return self._data["sprite"]["frame_height"]

    @property
    def animations(self) -> dict:
        return self._data["sprite"]["animations"]

    @property
    def size(self) -> int:
        return self._data["size"]

    @size.setter
    def size(self, value: int) -> None:
        self._data["size"] = value

    @property
    def poll_interval_ms(self) -> int:
        return self._data["poll_interval_ms"]

    @property
    def config_dir(self) -> Path:
        return self._config_dir
```

- [ ] **Step 4: 테스트 실행하여 통과 확인**

Run: `python -m pytest tests/test_config.py -v`
Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add watchingai/config.py tests/test_config.py
git commit -m "feat: 설정 모듈 구현 (config.py)"
```

---

### Task 3: 상태 파일 폴링 모듈 (status.py)

**Files:**
- Create: `watchingai/status.py`
- Create: `tests/test_status.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_status.py
import json
import time
from pathlib import Path
from datetime import datetime

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
    old_time = "2020-01-01T00:00:00"
    status_file = tmp_path / "status.json"
    status_file.write_text(json.dumps({
        "status": "working",
        "detail": "something",
        "timestamp": old_time,
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
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_status.py -v`
Expected: FAIL — `No module named 'watchingai.status'`

- [ ] **Step 3: status.py 구현**

```python
# watchingai/status.py
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
```

- [ ] **Step 4: 테스트 실행하여 통과 확인**

Run: `python -m pytest tests/test_status.py -v`
Expected: 5 passed

- [ ] **Step 5: 커밋**

```bash
git add watchingai/status.py tests/test_status.py
git commit -m "feat: 상태 파일 폴링 모듈 구현 (status.py)"
```

---

### Task 4: 스프라이트 시트 모듈 (sprite.py)

**Files:**
- Create: `watchingai/sprite.py`
- Create: `tests/test_sprite.py`
- Create: `assets/default_sprite.png` (플레이스홀더)

- [ ] **Step 1: 테스트용 스프라이트 시트 생성 헬퍼 및 실패하는 테스트 작성**

```python
# tests/test_sprite.py
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QColor
from PyQt6.QtCore import Qt
import sys

app = QApplication.instance() or QApplication(sys.argv)


def create_test_sprite_sheet(path: Path, cols: int = 4, rows: int = 3,
                              frame_w: int = 32, frame_h: int = 32) -> Path:
    img = QImage(cols * frame_w, rows * frame_h, QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))
    painter = QPainter(img)
    colors = [
        QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
        QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255),
    ]
    for r in range(rows):
        for c in range(cols):
            color = colors[(r * cols + c) % len(colors)]
            painter.fillRect(c * frame_w, r * frame_h, frame_w, frame_h, color)
    painter.end()
    file_path = path / "test_sheet.png"
    img.save(str(file_path))
    return file_path


def test_load_sprite_sheet(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    assert sheet.rows == 3
    assert sheet.cols == 4


def test_get_frame(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frame = sheet.get_frame(row=1, col=1)
    assert frame is not None
    assert frame.width() == 32
    assert frame.height() == 32


def test_get_frame_out_of_bounds_returns_none(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frame = sheet.get_frame(row=99, col=99)
    assert frame is None


def test_get_animation_frames(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frames = sheet.get_animation_frames(row=2, columns=[1, 2, 3])
    assert len(frames) == 3
    for f in frames:
        assert f.width() == 32


def test_get_animation_frames_skips_out_of_bounds(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frames = sheet.get_animation_frames(row=1, columns=[1, 2, 99])
    assert len(frames) == 2
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_sprite.py -v`
Expected: FAIL — `No module named 'watchingai.sprite'`

- [ ] **Step 3: sprite.py 구현**

```python
# watchingai/sprite.py
from pathlib import Path
from PyQt6.QtGui import QPixmap, QImage


class SpriteSheet:
    def __init__(self, path: Path, frame_width: int, frame_height: int):
        self._image = QImage(str(path))
        self._frame_width = frame_width
        self._frame_height = frame_height

    @property
    def rows(self) -> int:
        return self._image.height() // self._frame_height

    @property
    def cols(self) -> int:
        return self._image.width() // self._frame_width

    def get_frame(self, row: int, col: int) -> QPixmap | None:
        if row < 1 or col < 1 or row > self.rows or col > self.cols:
            return None
        x = (col - 1) * self._frame_width
        y = (row - 1) * self._frame_height
        cropped = self._image.copy(x, y, self._frame_width, self._frame_height)
        return QPixmap.fromImage(cropped)

    def get_animation_frames(self, row: int, columns: list[int]) -> list[QPixmap]:
        frames = []
        for col in columns:
            frame = self.get_frame(row, col)
            if frame is not None:
                frames.append(frame)
        return frames
```

- [ ] **Step 4: 테스트 실행하여 통과 확인**

Run: `python -m pytest tests/test_sprite.py -v`
Expected: 5 passed

- [ ] **Step 5: 디폴트 스프라이트 시트 플레이스홀더 생성**

`assets/` 디렉토리를 만들고 사용자가 제공한 `images/cat_01.jpg`를 `assets/default_sprite.png`로 복사한다. (실제 운영 시 적절한 라이선스의 스프라이트 시트로 교체)

Run: `mkdir -p assets && cp images/cat_01.jpg assets/default_sprite.png`

- [ ] **Step 6: 커밋**

```bash
git add watchingai/sprite.py tests/test_sprite.py assets/
git commit -m "feat: 스프라이트 시트 모듈 구현 (sprite.py)"
```

---

### Task 5: 투명 위젯 창 (widget.py)

**Files:**
- Create: `watchingai/widget.py`
- Create: `tests/test_widget.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_widget.py
import sys
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

app = QApplication.instance() or QApplication(sys.argv)


def test_widget_is_frameless():
    from watchingai.widget import SpriteWidget
    widget = SpriteWidget()
    flags = widget.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint
    widget.close()


def test_widget_is_always_on_top():
    from watchingai.widget import SpriteWidget
    widget = SpriteWidget()
    flags = widget.windowFlags()
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    widget.close()


def test_widget_has_transparent_background():
    from watchingai.widget import SpriteWidget
    widget = SpriteWidget()
    assert widget.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    widget.close()


def test_widget_is_draggable():
    from watchingai.widget import SpriteWidget
    widget = SpriteWidget()
    assert hasattr(widget, "mousePressEvent")
    assert hasattr(widget, "mouseMoveEvent")
    widget.close()


def test_widget_set_position_preset():
    from watchingai.widget import SpriteWidget
    widget = SpriteWidget()
    widget.set_position_preset("top-left")
    pos = widget.pos()
    assert pos.x() >= 0
    assert pos.y() >= 0
    widget.close()


def test_widget_update_sprite():
    from watchingai.widget import SpriteWidget
    from PyQt6.QtGui import QPixmap
    widget = SpriteWidget()
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.red)
    widget.update_sprite(pixmap)
    widget.close()
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_widget.py -v`
Expected: FAIL — `No module named 'watchingai.widget'`

- [ ] **Step 3: widget.py 구현**

```python
# watchingai/widget.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QToolTip
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QScreen, QGuiApplication


POSITION_PRESETS = {
    "top-left": (0.02, 0.02),
    "top-right": (0.95, 0.02),
    "bottom-left": (0.02, 0.90),
    "bottom-right": (0.95, 0.90),
    "taskbar": (0.90, 0.95),
}


class SpriteWidget(QWidget):
    def __init__(self, size: int = 64):
        super().__init__()
        self._size = size
        self._drag_pos = QPoint()
        self._tooltip_text = ""

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._label = QLabel(self)
        self._label.setFixedSize(size, size)
        self._label.setScaledContents(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        self.setFixedSize(size, size)

    def update_sprite(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(
            self._size, self._size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation,
        )
        self._label.setPixmap(scaled)

    def set_tooltip_text(self, text: str) -> None:
        self._tooltip_text = text
        self.setToolTip(text)

    def set_position_preset(self, preset: str) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        ratios = POSITION_PRESETS.get(preset, POSITION_PRESETS["bottom-right"])
        x = int(geo.x() + geo.width() * ratios[0])
        y = int(geo.y() + geo.height() * ratios[1])
        self.move(x, y)

    def set_custom_position(self, x: int, y: int) -> None:
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
```

- [ ] **Step 4: 테스트 실행하여 통과 확인**

Run: `python -m pytest tests/test_widget.py -v`
Expected: 6 passed

- [ ] **Step 5: 커밋**

```bash
git add watchingai/widget.py tests/test_widget.py
git commit -m "feat: 투명 위젯 창 구현 (widget.py)"
```

---

### Task 6: 시스템 트레이 메뉴 (tray.py)

**Files:**
- Create: `watchingai/tray.py`
- Create: `tests/test_tray.py`

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/test_tray.py
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)


def test_tray_has_menu():
    from watchingai.tray import TrayIcon
    from watchingai.config import Config
    config = Config(config_dir=Path(sys.argv[0]).parent / "_test_tray")
    tray = TrayIcon(config)
    menu = tray.contextMenu()
    assert menu is not None
    config._config_dir.exists() and __import__("shutil").rmtree(config._config_dir, ignore_errors=True)


def test_tray_menu_has_position_presets():
    from watchingai.tray import TrayIcon
    from watchingai.config import Config
    config = Config(config_dir=Path(sys.argv[0]).parent / "_test_tray2")
    tray = TrayIcon(config)
    menu = tray.contextMenu()
    action_texts = [a.text() for a in menu.actions()]
    assert any("위치" in t or "Position" in t for t in action_texts)
    config._config_dir.exists() and __import__("shutil").rmtree(config._config_dir, ignore_errors=True)


def test_tray_menu_has_quit():
    from watchingai.tray import TrayIcon
    from watchingai.config import Config
    config = Config(config_dir=Path(sys.argv[0]).parent / "_test_tray3")
    tray = TrayIcon(config)
    menu = tray.contextMenu()
    action_texts = [a.text() for a in menu.actions()]
    assert any("종료" in t or "Quit" in t for t in action_texts)
    config._config_dir.exists() and __import__("shutil").rmtree(config._config_dir, ignore_errors=True)
```

- [ ] **Step 2: 테스트 실행하여 실패 확인**

Run: `python -m pytest tests/test_tray.py -v`
Expected: FAIL — `No module named 'watchingai.tray'`

- [ ] **Step 3: tray.py 구현**

```python
# watchingai/tray.py
from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QFileDialog, QApplication,
)
from PyQt6.QtGui import QIcon, QPixmap, QAction
from PyQt6.QtCore import pyqtSignal, QObject

from watchingai.config import Config


class TrayIcon(QSystemTrayIcon):
    position_changed = pyqtSignal(str)
    size_changed = pyqtSignal(int)
    sprite_changed = pyqtSignal(str)
    quit_requested = pyqtSignal()

    def __init__(self, config: Config):
        icon = QPixmap(16, 16)
        icon.fill()
        super().__init__(QIcon(icon))
        self._config = config
        self._build_menu()

    def _build_menu(self) -> None:
        menu = QMenu()

        position_menu = menu.addMenu("위치 (Position)")
        presets = {
            "top-left": "좌상단",
            "top-right": "우상단",
            "bottom-left": "좌하단",
            "bottom-right": "우하단",
            "taskbar": "작업표시줄 근처",
        }
        for key, label in presets.items():
            action = position_menu.addAction(label)
            action.triggered.connect(lambda checked, k=key: self._on_position(k))

        size_menu = menu.addMenu("크기 (Size)")
        for s in [32, 48, 64, 96, 128]:
            action = size_menu.addAction(f"{s}x{s}")
            action.triggered.connect(lambda checked, sz=s: self._on_size(sz))

        sprite_action = menu.addAction("스프라이트 변경 (Change Sprite)")
        sprite_action.triggered.connect(self._on_change_sprite)

        menu.addSeparator()

        quit_action = menu.addAction("종료 (Quit)")
        quit_action.triggered.connect(self._on_quit)

        self.setContextMenu(menu)

    def _on_position(self, preset: str) -> None:
        self._config.position_preset = preset
        self._config.custom_position = None
        self._config.save()
        self.position_changed.emit(preset)

    def _on_size(self, size: int) -> None:
        self._config.size = size
        self._config.save()
        self.size_changed.emit(size)

    def _on_change_sprite(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            None, "스프라이트 시트 선택", "",
            "Images (*.png *.jpg *.bmp)"
        )
        if path:
            self._config.sprite_sheet = path
            self._config.save()
            self.sprite_changed.emit(path)

    def _on_quit(self) -> None:
        self.quit_requested.emit()
```

- [ ] **Step 4: 테스트 실행하여 통과 확인**

Run: `python -m pytest tests/test_tray.py -v`
Expected: 3 passed

- [ ] **Step 5: 커밋**

```bash
git add watchingai/tray.py tests/test_tray.py
git commit -m "feat: 시스템 트레이 메뉴 구현 (tray.py)"
```

---

### Task 7: 메인 앱 통합 (__main__.py)

**Files:**
- Modify: `watchingai/__main__.py`

- [ ] **Step 1: __main__.py 전체 구현**

```python
# watchingai/__main__.py
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap

from watchingai.config import Config
from watchingai.status import StatusReader, Status, IDLE
from watchingai.sprite import SpriteSheet
from watchingai.widget import SpriteWidget
from watchingai.tray import TrayIcon


STATE_LABELS = {
    "idle": "대기 중",
    "thinking": "생각 중",
    "working": "작업 중",
    "done": "완료",
    "error": "에러",
}


class WatchingAIApp:
    def __init__(self):
        self._config = Config()
        self._status_reader = StatusReader(status_dir=self._config.config_dir)
        self._sprite_sheet = self._load_sprite_sheet()
        self._widget = SpriteWidget(size=self._config.size)
        self._tray = TrayIcon(self._config)
        self._current_status = IDLE
        self._frame_index = 0
        self._current_frames: list[QPixmap] = []

        self._tray.position_changed.connect(self._on_position_changed)
        self._tray.size_changed.connect(self._on_size_changed)
        self._tray.sprite_changed.connect(self._on_sprite_changed)
        self._tray.quit_requested.connect(self._on_quit)

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._poll_status)
        self._status_timer.start(self._config.poll_interval_ms)

        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._next_frame)
        self._anim_timer.start(200)

        self._apply_position()
        self._update_animation(IDLE)
        self._widget.show()
        self._tray.show()

    def _load_sprite_sheet(self) -> SpriteSheet:
        sheet_path = self._config.sprite_sheet
        path = Path(sheet_path)
        if not path.is_absolute():
            candidate = self._config.config_dir / sheet_path
            if candidate.exists():
                path = candidate
            else:
                path = Path(__file__).parent.parent / "assets" / sheet_path
        return SpriteSheet(path,
                           self._config.frame_width,
                           self._config.frame_height)

    def _apply_position(self) -> None:
        custom = self._config.custom_position
        if custom:
            self._widget.set_custom_position(*custom)
        else:
            self._widget.set_position_preset(self._config.position_preset)

    def _poll_status(self) -> None:
        status = self._status_reader.read()
        if status != self._current_status:
            self._current_status = status
            self._update_animation(status)
        self._update_tooltip(status)

    def _update_animation(self, status: Status) -> None:
        state = status.state
        anim_config = self._config.animations.get(state)
        if anim_config is None:
            anim_config = self._config.animations.get("idle", {"row": 1, "columns": [1]})
        self._current_frames = self._sprite_sheet.get_animation_frames(
            row=anim_config["row"],
            columns=anim_config["columns"],
        )
        self._frame_index = 0
        if self._current_frames:
            self._widget.update_sprite(self._current_frames[0])

    def _next_frame(self) -> None:
        if not self._current_frames:
            return
        self._frame_index = (self._frame_index + 1) % len(self._current_frames)
        self._widget.update_sprite(self._current_frames[self._frame_index])

    def _update_tooltip(self, status: Status) -> None:
        label = STATE_LABELS.get(status.state, status.state)
        if status.detail:
            text = f"{label} — {status.detail} ({status.elapsed_seconds}초)"
        else:
            text = label
        self._widget.set_tooltip_text(text)

    def _on_position_changed(self, preset: str) -> None:
        self._widget.set_position_preset(preset)

    def _on_size_changed(self, size: int) -> None:
        self._widget.close()
        self._widget = SpriteWidget(size=size)
        self._apply_position()
        self._update_animation(self._current_status)
        self._widget.show()

    def _on_sprite_changed(self, path: str) -> None:
        self._sprite_sheet = SpriteSheet(
            Path(path), self._config.frame_width, self._config.frame_height
        )
        self._update_animation(self._current_status)

    def _on_quit(self) -> None:
        custom_pos = self._widget.pos()
        self._config.custom_position = (custom_pos.x(), custom_pos.y())
        self._config.save()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    wai = WatchingAIApp()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: 수동 실행 테스트**

Run: `python -m watchingai`
Expected: 화면 우하단에 스프라이트 위젯이 나타나고, 시스템 트레이에 아이콘이 표시됨. 드래그로 이동 가능. 트레이 우클릭으로 메뉴 확인.

- [ ] **Step 3: 커밋**

```bash
git add watchingai/__main__.py
git commit -m "feat: 메인 앱 통합 (__main__.py)"
```

---

### Task 8: Claude Code 플러그인 구현

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `hooks/hooks.json`
- Create: `bin/watchingai-status.sh`
- Create: `setup.sh`

- [ ] **Step 1: plugin.json 생성**

```json
{
  "name": "watchingai",
  "description": "Desktop sprite widget that shows Claude Code's working status",
  "version": "0.1.0",
  "author": {
    "name": "WatchingAI"
  },
  "homepage": "https://github.com/watchingai/watchingai",
  "license": "MIT",
  "setup": "setup.sh"
}
```

- [ ] **Step 2: 상태 기록 스크립트 생성 (bin/watchingai-status.sh)**

```bash
#!/bin/bash
set -euo pipefail

WATCHINGAI_DIR="$HOME/.watchingai"
STATUS_FILE="$WATCHINGAI_DIR/status.json"
mkdir -p "$WATCHINGAI_DIR"

HOOK_INPUT=$(cat)
HOOK_EVENT=$(echo "$HOOK_INPUT" | jq -r '.hook_event_name // empty')
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$HOOK_INPUT" | jq -r '.tool_input // empty')

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S")

write_status() {
    local status="$1"
    local detail="$2"
    cat > "$STATUS_FILE" << STATUSEOF
{
  "status": "$status",
  "detail": "$detail",
  "timestamp": "$TIMESTAMP",
  "elapsed_seconds": 0
}
STATUSEOF
}

case "$HOOK_EVENT" in
    "SessionStart")
        write_status "idle" ""
        ;;
    "UserPromptSubmit")
        write_status "thinking" "요청 처리 중..."
        ;;
    "PreToolUse")
        case "$TOOL_NAME" in
            "Edit"|"Write")
                FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // "unknown"')
                write_status "working" "$FILE_PATH 편집 중"
                ;;
            "Bash"|"PowerShell")
                COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // ""' | head -c 50)
                write_status "working" "명령 실행: $COMMAND"
                ;;
            "Read"|"Glob"|"Grep")
                write_status "working" "파일 탐색 중"
                ;;
            *)
                write_status "working" "$TOOL_NAME 실행 중"
                ;;
        esac
        ;;
    "PostToolUse")
        write_status "done" "완료"
        ;;
    "PostToolUseFailure")
        write_status "error" "$TOOL_NAME 실패"
        ;;
    "Stop")
        write_status "idle" ""
        ;;
    "SessionEnd")
        write_status "idle" ""
        ;;
esac

exit 0
```

- [ ] **Step 3: hooks.json 생성**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/watchingai-status.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/watchingai-status.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/watchingai-status.sh"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/watchingai-status.sh"
          }
        ]
      }
    ],
    "PostToolUseFailure": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/watchingai-status.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/watchingai-status.sh"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/bin/watchingai-status.sh"
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: setup.sh 생성**

```bash
#!/bin/bash
set -euo pipefail

echo "=== WatchingAI Setup ==="

WATCHINGAI_DIR="$HOME/.watchingai"
mkdir -p "$WATCHINGAI_DIR"

# 디폴트 스프라이트 시트 복사
if [ -f "${CLAUDE_PLUGIN_ROOT}/assets/default_sprite.png" ]; then
    cp "${CLAUDE_PLUGIN_ROOT}/assets/default_sprite.png" "$WATCHINGAI_DIR/"
fi

# Python 설치 확인
if command -v python3 &> /dev/null || command -v python &> /dev/null; then
    PYTHON_CMD=$(command -v python3 || command -v python)
    echo "Python found: $PYTHON_CMD"
    echo "Installing watchingai via pip..."
    "$PYTHON_CMD" -m pip install watchingai
    echo "Starting WatchingAI..."
    "$PYTHON_CMD" -m watchingai &
else
    echo "Python not found. Downloading standalone exe..."
    RELEASE_URL="https://github.com/watchingai/watchingai/releases/latest/download/watchingai-windows.exe"
    EXE_PATH="$WATCHINGAI_DIR/watchingai.exe"
    curl -L -o "$EXE_PATH" "$RELEASE_URL"
    chmod +x "$EXE_PATH"
    echo "Starting WatchingAI..."
    "$EXE_PATH" &
fi

echo "=== WatchingAI Setup Complete ==="
```

- [ ] **Step 5: 스크립트 실행 권한 부여**

Run: `chmod +x bin/watchingai-status.sh setup.sh`

- [ ] **Step 6: 커밋**

```bash
git add .claude-plugin/ hooks/ bin/ setup.sh
git commit -m "feat: Claude Code 플러그인 구현 (hooks, setup)"
```

---

### Task 9: PyInstaller exe 빌드 설정

**Files:**
- Create: `watchingai.spec` (또는 빌드 스크립트)
- Create: `build.sh`

- [ ] **Step 1: build.sh 생성**

```bash
#!/bin/bash
set -euo pipefail

echo "=== Building WatchingAI exe ==="

pip install pyinstaller

pyinstaller \
    --name watchingai \
    --onefile \
    --windowed \
    --add-data "assets/default_sprite.png:assets" \
    --icon assets/default_sprite.png \
    watchingai/__main__.py

echo "=== Build complete: dist/watchingai.exe ==="
```

- [ ] **Step 2: 빌드 실행 테스트**

Run: `bash build.sh`
Expected: `dist/watchingai.exe` 파일이 생성됨

- [ ] **Step 3: exe 실행 테스트**

Run: `./dist/watchingai.exe`
Expected: 스프라이트 위젯이 정상적으로 나타남

- [ ] **Step 4: 커밋**

```bash
git add build.sh
git commit -m "feat: PyInstaller 빌드 스크립트 추가"
```

---

### Task 10: 통합 테스트 및 최종 확인

**Files:**
- 기존 파일 수정 없음, 전체 흐름 테스트

- [ ] **Step 1: 전체 테스트 스위트 실행**

Run: `python -m pytest tests/ -v`
Expected: 모든 테스트 통과

- [ ] **Step 2: 플러그인 로컬 테스트**

Run: `claude --plugin-dir .`
Claude Code에서 작업 수행 후 `~/.watchingai/status.json` 파일이 갱신되는지 확인.

- [ ] **Step 3: 데스크톱 앱 + 플러그인 통합 테스트**

1. 터미널 1: `python -m watchingai` 실행
2. 터미널 2: `claude --plugin-dir .` 로 Claude Code 시작
3. Claude Code에서 아무 작업 수행
4. 확인 사항:
   - 고양이 스프라이트가 상태에 따라 변하는지
   - 호버 시 툴팁에 작업 내용이 표시되는지
   - 드래그로 위치 이동이 되는지
   - 트레이 메뉴에서 위치 프리셋 변경이 되는지
   - 트레이 메뉴에서 크기 변경이 되는지
   - 종료 후 위치가 저장되는지

- [ ] **Step 4: 최종 커밋**

```bash
git add -A
git commit -m "chore: 통합 테스트 완료"
```
