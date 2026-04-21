import argparse
import json
import os
import sys
from datetime import datetime, timezone
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
    def __init__(self, project_id: str | None = None):
        self._project_id = project_id
        self._config = Config(project_id=project_id)
        self._status_reader = StatusReader(
            status_dir=self._config.config_dir,
            project_id=project_id,
        )
        self._assets_dir = Path(__file__).parent / "assets"
        self._frame_loader = FrameLoader(
            frames_dir=self._config.frames_dir,
            assets_dir=self._assets_dir,
        )
        self._project_name = self._read_project_name()
        self._widget = SpriteWidget(ratio=self._config.size_ratio)
        self._tray = TrayIcon(self._config, project_name=self._project_name)
        self._current_status = IDLE
        self._frame_index = 0
        self._current_frames: list[QPixmap] = []

        self._config.frames_dir.mkdir(parents=True, exist_ok=True)

        self._tray.position_changed.connect(self._on_position_changed)
        self._tray.size_changed.connect(self._on_size_changed)
        self._tray.frames_changed.connect(self._on_frames_changed)
        self._tray.test_state_changed.connect(self._on_test_state)
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
        self._write_pid()

    def _read_project_name(self) -> str:
        if not self._project_id:
            return ""
        path_file = self._config.config_dir / f"project_{self._project_id}.path"
        try:
            project_path = path_file.read_text(encoding="utf-8").strip()
            return Path(project_path).name
        except (FileNotFoundError, OSError):
            return ""

    def _pid_file(self) -> Path:
        name = f"pid_{self._project_id}.txt" if self._project_id else "pid.txt"
        return self._config.config_dir / name

    def _write_pid(self) -> None:
        import os
        self._pid_file().write_text(str(os.getpid()), encoding="utf-8")

    def _remove_pid(self) -> None:
        try:
            self._pid_file().unlink()
        except FileNotFoundError:
            pass

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
            if status.detail and status.detail.startswith("[세션종료]"):
                msg = status.detail.replace("[세션종료] ", "")
                self._widget.show_bubble(msg, 8000)
        self._update_tooltip(status)

    def _update_animation(self, status: Status) -> None:
        state = status.state
        frame_files = self._config.animations.get(state)
        if not frame_files:
            frame_files = self._config.animations.get("idle", [])

        if len(frame_files) == 1 and frame_files[0].lower().endswith(".gif"):
            gif_path = self._frame_loader.resolve_path(frame_files[0])
            if gif_path.exists():
                self._current_frames = []
                self._widget.play_gif(str(gif_path))
                return

        self._widget.stop_gif()
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
            text = f"{label} — {status.detail}"
        else:
            text = label
        self._widget.set_tooltip_text(text)

    def _on_position_changed(self, preset: str) -> None:
        self._widget.set_position_preset(preset)

    def _on_size_changed(self, ratio: float) -> None:
        self._widget.close()
        self._widget = SpriteWidget(ratio=ratio)
        self._apply_position()
        self._update_animation(self._current_status)
        self._widget.show()

    def _on_frames_changed(self) -> None:
        self._update_animation(self._current_status)

    def _on_test_state(self, state: str) -> None:
        if self._project_id:
            status_file = self._config.config_dir / f"status_{self._project_id}.json"
        else:
            status_file = self._config.config_dir / "status.json"
        data = {
            "status": state,
            "detail": f"테스트: {STATE_LABELS.get(state, state)}",
            "elapsed_seconds": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        status_file.parent.mkdir(parents=True, exist_ok=True)
        with open(status_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        test_status = Status(state=state, detail=data["detail"], elapsed_seconds=0)
        self._current_status = test_status
        self._update_animation(test_status)
        self._update_tooltip(test_status)

    def _on_quit(self) -> None:
        custom_pos = self._widget.pos()
        self._config.custom_position = (custom_pos.x(), custom_pos.y())
        self._config.save()
        self._remove_pid()
        QApplication.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=None)
    args, remaining = parser.parse_known_args()

    if sys.platform == "darwin":
        os.environ.setdefault("QT_MAC_WANTS_LAYER", "1")

    app = QApplication(remaining)
    app.setQuitOnLastWindowClosed(False)
    _wai = WatchingAIApp(project_id=args.project_id)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
