from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QFileDialog
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal

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
