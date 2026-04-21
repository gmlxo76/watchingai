import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

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
    widget = SpriteWidget()
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.red)
    widget.update_sprite(pixmap)
    widget.close()
