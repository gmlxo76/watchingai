import sys

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer, QSize
from PyQt6.QtGui import QCursor, QPixmap, QGuiApplication, QFont, QMovie

_FONT_FAMILY = "Helvetica Neue" if sys.platform == "darwin" else "맑은 고딕"


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
        if sys.platform == "darwin":
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)

        self._label = QLabel(self)
        self._label.setStyleSheet(
            "background-color: rgba(30, 30, 30, 220);"
            "color: white;"
            "padding: 6px 10px;"
            "border-radius: 6px;"
            "font-size: 12px;"
        )
        self._label.setFont(QFont(_FONT_FAMILY, 9))

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


class BubbleWindow(QWidget):
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
        if sys.platform == "darwin":
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)

        self._label = QLabel(self)
        self._label.setStyleSheet(
            "background-color: white;"
            "color: #333;"
            "padding: 8px 12px;"
            "border-radius: 10px;"
            "border: 2px solid #ccc;"
            "font-size: 12px;"
        )
        self._label.setFont(QFont(_FONT_FAMILY, 9))
        self._label.setWordWrap(True)
        self._label.setMaximumWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    def show_message(self, text: str, widget_pos: QPoint, widget_w: int, duration_ms: int = 5000) -> None:
        self._label.setText(text)
        self._label.adjustSize()
        self.adjustSize()
        x = widget_pos.x() + widget_w + 8
        y = widget_pos.y()
        screen = QGuiApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            if x + self.width() > geo.x() + geo.width():
                x = widget_pos.x() - self.width() - 8
            if y < geo.y():
                y = geo.y() + 4
            if y + self.height() > geo.y() + geo.height():
                y = geo.y() + geo.height() - self.height() - 4
        self.move(x, y)
        self.show()
        if duration_ms > 0:
            self._hide_timer.start(duration_ms)


class SpriteWidget(QWidget):
    def __init__(self, ratio: float = 1.0):
        super().__init__()
        self._ratio = ratio
        self._display_w = 128
        self._display_h = 128
        self._drag_pos = QPoint()
        self._hovering = False
        self._tooltip_text = ""

        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        if sys.platform == "darwin":
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow)
        self.setMouseTracking(True)

        self._label = QLabel(self)
        self._label.setScaledContents(True)
        self._label.setMouseTracking(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)

        self._movie = None
        self._tooltip_win = TooltipWindow()
        self._bubble_win = BubbleWindow()

    def play_gif(self, path: str) -> None:
        if self._movie:
            self._movie.stop()
        self._movie = QMovie(path)
        if not self._movie.isValid():
            self._movie = None
            return
        self._label.setScaledContents(True)
        orig = self._movie.scaledSize()
        if orig.isEmpty():
            self._movie.jumpToFrame(0)
            orig = self._movie.currentPixmap().size()
        self._display_w = max(1, int(orig.width() * self._ratio))
        self._display_h = max(1, int(orig.height() * self._ratio))
        self._movie.setScaledSize(QSize(self._display_w, self._display_h))
        self._label.setFixedSize(self._display_w, self._display_h)
        self.setFixedSize(self._display_w, self._display_h)
        self._label.setMovie(self._movie)
        self._movie.start()

    def stop_gif(self) -> None:
        if self._movie:
            self._movie.stop()
            self._movie = None

    def show_bubble(self, text: str, duration_ms: int = 5000) -> None:
        self._bubble_win.show_message(text, self.pos(), self._display_w, duration_ms)

    def _update_bubble_pos(self) -> None:
        if self._bubble_win.isVisible():
            self._bubble_win.show_message(
                self._bubble_win._label.text(),
                self.pos(), self._display_w,
                0,
            )

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
            self._update_bubble_pos()
            event.accept()
        if self._hovering and self._tooltip_text:
            self._tooltip_win.show_at_cursor(event.globalPosition().toPoint())

    def closeEvent(self, event):
        self._tooltip_win.close()
        self._bubble_win.close()
        super().closeEvent(event)
