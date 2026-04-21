from pathlib import Path

from PyQt6.QtGui import QPixmap, QImage


class SpriteSheet:
    def __init__(self, path: Path, frame_width: int, frame_height: int):
        self._image = QImage(str(path))
        self._frame_width = frame_width
        self._frame_height = frame_height

    @property
    def rows(self) -> int:
        return self._image.height() // self._frame_height

    @property
    def cols(self) -> int:
        return self._image.width() // self._frame_width

    def get_frame(self, row: int, col: int) -> QPixmap | None:
        if row < 1 or col < 1 or row > self.rows or col > self.cols:
            return None
        x = (col - 1) * self._frame_width
        y = (row - 1) * self._frame_height
        cropped = self._image.copy(x, y, self._frame_width, self._frame_height)
        return QPixmap.fromImage(cropped)

    def get_animation_frames(self, row: int, columns: list[int]) -> list[QPixmap]:
        frames = []
        for col in columns:
            frame = self.get_frame(row, col)
            if frame is not None:
                frames.append(frame)
        return frames
