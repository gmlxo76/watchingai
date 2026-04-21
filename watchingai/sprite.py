from pathlib import Path

from PyQt6.QtGui import QPixmap, QMovie


class FrameLoader:
    def __init__(self, frames_dir: Path, assets_dir: Path | None = None):
        self._frames_dir = frames_dir
        self._assets_dir = assets_dir

    def resolve_path(self, filename: str) -> Path:
        candidate = self._frames_dir / filename
        if candidate.exists():
            return candidate
        if self._assets_dir:
            candidate = self._assets_dir / filename
            if candidate.exists():
                return candidate
        return self._frames_dir / filename

    def load_frames(self, filenames: list[str]) -> list[QPixmap]:
        frames = []
        for name in filenames:
            path = self.resolve_path(name)
            if path.exists():
                if path.suffix.lower() == ".gif":
                    pass
                else:
                    pixmap = QPixmap(str(path))
                    if not pixmap.isNull():
                        frames.append(pixmap)
        return frames

    def list_available_frames(self) -> list[str]:
        frames = []
        for d in [self._frames_dir, self._assets_dir]:
            if d and d.exists():
                for f in sorted(d.iterdir()):
                    if f.suffix.lower() in (".png", ".jpg", ".bmp", ".gif"):
                        if f.name not in frames:
                            frames.append(f.name)
        return sorted(set(frames))
