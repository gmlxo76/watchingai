from pathlib import Path

from PyQt6.QtWidgets import (
    QSystemTrayIcon, QMenu, QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QPushButton, QListWidgetItem, QComboBox,
    QFileDialog, QApplication,
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal, Qt

from watchingai.config import Config

STATE_NAMES = {
    "idle": "대기 중 (Idle)",
    "thinking": "생각 중 (Thinking)",
    "working": "작업 중 (Working)",
    "done": "완료 (Done)",
    "error": "에러 (Error)",
}


class FramePickerDialog(QDialog):
    def __init__(self, config: Config, frames_dir: Path, assets_dir: Path | None = None):
        super().__init__()
        self.setWindowTitle("프레임 설정 (Frame Settings)")
        self.setMinimumSize(500, 400)
        self._config = config
        self._frames_dir = frames_dir
        self._assets_dir = assets_dir

        layout = QVBoxLayout(self)

        self._state_combo = QComboBox()
        for key, label in STATE_NAMES.items():
            self._state_combo.addItem(label, key)
        self._state_combo.currentIndexChanged.connect(self._on_state_changed)
        layout.addWidget(QLabel("상태 선택:"))
        layout.addWidget(self._state_combo)

        mid = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("사용 가능한 프레임:"))
        self._available_list = QListWidget()
        self._available_list.setIconSize(self._available_list.iconSize().__class__(64, 64))
        left_layout.addWidget(self._available_list)
        mid.addLayout(left_layout)

        btn_layout = QVBoxLayout()
        btn_layout.addStretch()
        add_btn = QPushButton("→ 추가")
        add_btn.clicked.connect(self._add_frame)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton("← 제거")
        remove_btn.clicked.connect(self._remove_frame)
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        mid.addLayout(btn_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("선택된 프레임 (애니메이션 순서):"))
        self._selected_list = QListWidget()
        self._selected_list.setIconSize(self._selected_list.iconSize().__class__(64, 64))
        right_layout.addWidget(self._selected_list)

        order_layout = QHBoxLayout()
        up_btn = QPushButton("▲")
        up_btn.clicked.connect(self._move_up)
        order_layout.addWidget(up_btn)
        down_btn = QPushButton("▼")
        down_btn.clicked.connect(self._move_down)
        order_layout.addWidget(down_btn)
        right_layout.addLayout(order_layout)
        mid.addLayout(right_layout)

        layout.addLayout(mid)

        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self._save_and_close)
        layout.addWidget(save_btn)

        self._load_available_frames()
        self._on_state_changed()

    def _get_all_frame_files(self) -> list[Path]:
        files = []
        for d in [self._frames_dir, self._assets_dir]:
            if d and d.exists():
                for f in sorted(d.iterdir()):
                    if f.suffix.lower() in (".png", ".jpg", ".bmp"):
                        if not any(ef.name == f.name for ef in files):
                            files.append(f)
        return sorted(files, key=lambda p: p.name)

    def _load_available_frames(self) -> None:
        self._available_list.clear()
        for f in self._get_all_frame_files():
            item = QListWidgetItem(f.name)
            pixmap = QPixmap(str(f))
            if not pixmap.isNull():
                item.setIcon(QIcon(pixmap))
            item.setData(Qt.ItemDataRole.UserRole, f.name)
            self._available_list.addItem(item)

    def _on_state_changed(self) -> None:
        state = self._state_combo.currentData()
        self._selected_list.clear()
        current_frames = self._config.animations.get(state, [])
        for name in current_frames:
            item = QListWidgetItem(name)
            path = self._resolve_frame(name)
            if path and path.exists():
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap))
            item.setData(Qt.ItemDataRole.UserRole, name)
            self._selected_list.addItem(item)

    def _resolve_frame(self, name: str) -> Path | None:
        for d in [self._frames_dir, self._assets_dir]:
            if d:
                p = d / name
                if p.exists():
                    return p
        return None

    def _add_frame(self) -> None:
        item = self._available_list.currentItem()
        if item:
            name = item.data(Qt.ItemDataRole.UserRole)
            new_item = QListWidgetItem(name)
            path = self._resolve_frame(name)
            if path and path.exists():
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    new_item.setIcon(QIcon(pixmap))
            new_item.setData(Qt.ItemDataRole.UserRole, name)
            self._selected_list.addItem(new_item)

    def _remove_frame(self) -> None:
        row = self._selected_list.currentRow()
        if row >= 0:
            self._selected_list.takeItem(row)

    def _move_up(self) -> None:
        row = self._selected_list.currentRow()
        if row > 0:
            item = self._selected_list.takeItem(row)
            self._selected_list.insertItem(row - 1, item)
            self._selected_list.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self._selected_list.currentRow()
        if row < self._selected_list.count() - 1:
            item = self._selected_list.takeItem(row)
            self._selected_list.insertItem(row + 1, item)
            self._selected_list.setCurrentRow(row + 1)

    def _save_and_close(self) -> None:
        state = self._state_combo.currentData()
        frames = []
        for i in range(self._selected_list.count()):
            item = self._selected_list.item(i)
            frames.append(item.data(Qt.ItemDataRole.UserRole))
        self._config.animations[state] = frames
        self._config.save()
        self.accept()


class TrayIcon(QSystemTrayIcon):
    position_changed = pyqtSignal(str)
    size_changed = pyqtSignal(int)
    frames_changed = pyqtSignal()
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

        frame_action = menu.addAction("프레임 설정 (Frame Settings)")
        frame_action.triggered.connect(self._on_frame_settings)

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

    def _on_frame_settings(self) -> None:
        assets_dir = Path(__file__).parent.parent / "assets"
        dialog = FramePickerDialog(
            self._config,
            frames_dir=self._config.frames_dir,
            assets_dir=assets_dir,
        )
        if dialog.exec():
            self.frames_changed.emit()

    def _on_quit(self) -> None:
        self.quit_requested.emit()
