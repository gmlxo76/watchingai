import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

app = QApplication.instance() or QApplication(sys.argv)


def test_tray_has_menu(tmp_path):
    from watchingai.tray import TrayIcon
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    tray = TrayIcon(config)
    menu = tray.contextMenu()
    assert menu is not None


def test_tray_menu_has_position_presets(tmp_path):
    from watchingai.tray import TrayIcon
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    tray = TrayIcon(config)
    menu = tray.contextMenu()
    action_texts = [a.text() for a in menu.actions()]
    assert any("위치" in t or "Position" in t for t in action_texts)


def test_tray_menu_has_quit(tmp_path):
    from watchingai.tray import TrayIcon
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    tray = TrayIcon(config)
    menu = tray.contextMenu()
    action_texts = [a.text() for a in menu.actions()]
    assert any("종료" in t or "Quit" in t for t in action_texts)
