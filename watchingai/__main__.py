import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap

from watchingai.config import Config
from watchingai.status import StatusReader, Status, IDLE
from watchingai.sprite import FrameLoader
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
        self._assets_dir = Path(__file__).parent.parent / "assets"
        self._frame_loader = FrameLoader(
            frames_dir=self._config.frames_dir,
            assets_dir=self._assets_dir,
        )
        self._widget = SpriteWidget(size=self._config.size)
        self._tray = TrayIcon(self._config)
        self._current_status = IDLE
        self._frame_index = 0
        self._current_frames: list[QPixmap] = []

        self._config.frames_dir.mkdir(parents=True, exist_ok=True)

        self._tray.position_changed.connect(self._on_position_changed)
        self._tray.size_changed.connect(self._on_size_changed)
        self._tray.frames_changed.connect(self._on_frames_changed)
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
        frame_files = self._config.animations.get(state)
        if not frame_files:
            frame_files = self._config.animations.get("idle", [])
        self._current_frames = self._frame_loader.load_frames(frame_files)
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

    def _on_frames_changed(self) -> None:
        self._update_animation(self._current_status)

    def _on_quit(self) -> None:
        custom_pos = self._widget.pos()
        self._config.custom_position = (custom_pos.x(), custom_pos.y())
        self._config.save()
        QApplication.quit()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    _wai = WatchingAIApp()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
