from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QCursor, QPixmap, QGuiApplication, QFont


POSITION_PRESETS = {
    "top-left": (0.02, 0.02),
    "top-right": (0.95, 0.02),
    "bottom-left": (0.02, 0.90),
    "bottom-right": (0.95, 0.90),
    "taskbar": (0.90, 0.95),
}


class TooltipWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._label = QLabel(self)
        self._label.setStyleSheet(
            "background-color: rgba(30, 30, 30, 220);"
            "color: white;"
            "padding: 6px 10px;"
            "border-radius: 6px;"
            "font-size: 12px;"
        )
        self._label.setFont(QFont("맑은 고딕", 9))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

    def update_text(self, text: str) -> None:
        self._label.setText(text)
        self._label.adjustSize()
        self.adjustSize()

    def show_at_cursor(self, cursor_pos: QPoint) -> None:
        x = cursor_pos.x() + 16
        y = cursor_pos.y() + 16
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            if y + self.height() > geo.y() + geo.height():
                y = cursor_pos.y() - self.height() - 4
            if x + self.width() > geo.x() + geo.width():
                x = cursor_pos.x() - self.width() - 4
        self.move(x, y)
        self.show()


class SpriteWidget(QWidget):
    def __init__(self, ratio: float = 1.0):
        super().__init__()
        self._ratio = ratio
        self._display_w = 128
        self._display_h = 128
        self._drag_pos = QPoint()
        self._hovering = False
        self._tooltip_text = ""

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self._label = QLabel(self)
        self._label.setScaledContents(True)
        self._label.setMouseTracking(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

        self._tooltip_win = TooltipWindow()

    def update_sprite(self, pixmap: QPixmap) -> None:
        self._display_w = max(1, int(pixmap.width() * self._ratio))
        self._display_h = max(1, int(pixmap.height() * self._ratio))
        self._label.setFixedSize(self._display_w, self._display_h)
        self.setFixedSize(self._display_w, self._display_h)
        scaled = pixmap.scaled(
            self._display_w, self._display_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)

    def set_tooltip_text(self, text: str) -> None:
        self._tooltip_text = text
        if self._hovering:
            self._tooltip_win.update_text(text)
            self._tooltip_win.show_at_cursor(QCursor.pos())

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

    def enterEvent(self, event):
        self._hovering = True
        if self._tooltip_text:
            self._tooltip_win.update_text(self._tooltip_text)
            self._tooltip_win.show_at_cursor(QCursor.pos())
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovering = False
        self._tooltip_win.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        if self._hovering and self._tooltip_text:
            self._tooltip_win.show_at_cursor(event.globalPosition().toPoint())

    def closeEvent(self, event):
        self._tooltip_win.close()
        super().closeEvent(event)
