from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QGuiApplication


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
