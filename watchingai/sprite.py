from pathlib import Path

from PyQt6.QtGui import QPixmap, QImage, QColor
from PyQt6.QtCore import Qt


class SpriteSheet:
    def __init__(self, path: Path, rows: int = 0, cols: int = 0,
                 frame_width: int = 0, frame_height: int = 0,
                 transparent_color: QColor | None = None):
        self._image = QImage(str(path))
        if self._image.format() != QImage.Format.Format_ARGB32:
            self._image = self._image.convertToFormat(QImage.Format.Format_ARGB32)

        if frame_width > 0 and frame_height > 0:
            self._frame_width = frame_width
            self._frame_height = frame_height
        elif rows > 0 and cols > 0:
            self._frame_width = self._image.width() // cols
            self._frame_height = self._image.height() // rows
        else:
            self._auto_detect_grid()

        if transparent_color is None:
            corner = self._image.pixelColor(0, 0)
            if corner.lightness() > 200:
                transparent_color = corner
        if transparent_color is not None:
            self._apply_transparency(transparent_color)

    def _auto_detect_grid(self) -> None:
        w = self._image.width()
        h = self._image.height()
        bg = self._image.pixelColor(0, 0)
        threshold = 30

        col_splits = []
        for x in range(1, w):
            col_is_bg = True
            for y_sample in range(0, h, max(1, h // 20)):
                c = self._image.pixelColor(x, y_sample)
                if abs(c.red() - bg.red()) + abs(c.green() - bg.green()) + abs(c.blue() - bg.blue()) > threshold:
                    col_is_bg = False
                    break
            prev_is_bg = True
            for y_sample in range(0, h, max(1, h // 20)):
                c = self._image.pixelColor(x - 1, y_sample)
                if abs(c.red() - bg.red()) + abs(c.green() - bg.green()) + abs(c.blue() - bg.blue()) > threshold:
                    prev_is_bg = False
                    break
            if col_is_bg and not prev_is_bg:
                col_splits.append(x)

        row_splits = []
        for y in range(1, h):
            row_is_bg = True
            for x_sample in range(0, w, max(1, w // 20)):
                c = self._image.pixelColor(x_sample, y)
                if abs(c.red() - bg.red()) + abs(c.green() - bg.green()) + abs(c.blue() - bg.blue()) > threshold:
                    row_is_bg = False
                    break
            prev_is_bg = True
            for x_sample in range(0, w, max(1, w // 20)):
                c = self._image.pixelColor(x_sample, y - 1)
                if abs(c.red() - bg.red()) + abs(c.green() - bg.green()) + abs(c.blue() - bg.blue()) > threshold:
                    prev_is_bg = False
                    break
            if row_is_bg and not prev_is_bg:
                row_splits.append(y)

        num_cols = len(col_splits) + 1 if col_splits else 4
        num_rows = len(row_splits) + 1 if row_splits else 4
        self._frame_width = w // num_cols
        self._frame_height = h // num_rows

    def _apply_transparency(self, color: QColor, tolerance: int = 40) -> None:
        w = self._image.width()
        h = self._image.height()
        for y in range(h):
            for x in range(w):
                px = self._image.pixelColor(x, y)
                diff = (abs(px.red() - color.red())
                        + abs(px.green() - color.green())
                        + abs(px.blue() - color.blue()))
                if diff < tolerance:
                    self._image.setPixelColor(x, y, QColor(0, 0, 0, 0))

    @property
    def rows(self) -> int:
        return self._image.height() // self._frame_height

    @property
    def cols(self) -> int:
        return self._image.width() // self._frame_width

    @property
    def frame_width(self) -> int:
        return self._frame_width

    @property
    def frame_height(self) -> int:
        return self._frame_height

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
