import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QColor

app = QApplication.instance() or QApplication(sys.argv)


def create_test_sprite_sheet(path: Path, cols: int = 4, rows: int = 3,
                              frame_w: int = 32, frame_h: int = 32) -> Path:
    img = QImage(cols * frame_w, rows * frame_h, QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))
    painter = QPainter(img)
    colors = [
        QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255),
        QColor(255, 255, 0), QColor(255, 0, 255), QColor(0, 255, 255),
    ]
    for r in range(rows):
        for c in range(cols):
            color = colors[(r * cols + c) % len(colors)]
            painter.fillRect(c * frame_w, r * frame_h, frame_w, frame_h, color)
    painter.end()
    file_path = path / "test_sheet.png"
    img.save(str(file_path))
    return file_path


def test_load_sprite_sheet(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    assert sheet.rows == 3
    assert sheet.cols == 4


def test_get_frame(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frame = sheet.get_frame(row=1, col=1)
    assert frame is not None
    assert frame.width() == 32
    assert frame.height() == 32


def test_get_frame_out_of_bounds_returns_none(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frame = sheet.get_frame(row=99, col=99)
    assert frame is None


def test_get_animation_frames(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frames = sheet.get_animation_frames(row=2, columns=[1, 2, 3])
    assert len(frames) == 3
    for f in frames:
        assert f.width() == 32


def test_get_animation_frames_skips_out_of_bounds(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, frame_width=32, frame_height=32)
    frames = sheet.get_animation_frames(row=1, columns=[1, 2, 99])
    assert len(frames) == 2
