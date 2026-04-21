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


def test_load_sprite_sheet_with_rows_cols(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, rows=3, cols=4)
    assert sheet.rows == 3
    assert sheet.cols == 4
    assert sheet.frame_width == 32
    assert sheet.frame_height == 32


def test_get_frame(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, rows=3, cols=4)
    frame = sheet.get_frame(row=1, col=1)
    assert frame is not None
    assert frame.width() == 32
    assert frame.height() == 32


def test_get_frame_out_of_bounds_returns_none(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, rows=3, cols=4)
    frame = sheet.get_frame(row=99, col=99)
    assert frame is None


def test_get_animation_frames(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, rows=3, cols=4)
    frames = sheet.get_animation_frames(row=2, columns=[1, 2, 3])
    assert len(frames) == 3
    for f in frames:
        assert f.width() == 32


def test_get_animation_frames_skips_out_of_bounds(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path)
    sheet = SpriteSheet(sheet_path, rows=3, cols=4)
    frames = sheet.get_animation_frames(row=1, columns=[1, 2, 99])
    assert len(frames) == 2


def test_transparency_applied_for_light_bg(tmp_path):
    from watchingai.sprite import SpriteSheet
    img = QImage(64, 64, QImage.Format.Format_ARGB32)
    img.fill(QColor(255, 255, 255))
    painter = QPainter(img)
    painter.fillRect(10, 10, 20, 20, QColor(255, 0, 0))
    painter.end()
    file_path = tmp_path / "white_bg.png"
    img.save(str(file_path))

    sheet = SpriteSheet(file_path, rows=1, cols=1)
    frame = sheet.get_frame(1, 1)
    assert frame is not None
    frame_img = frame.toImage()
    assert frame_img.pixelColor(0, 0).alpha() == 0
    assert frame_img.pixelColor(15, 15).alpha() > 0


def test_auto_detect_grid(tmp_path):
    from watchingai.sprite import SpriteSheet
    sheet_path = create_test_sprite_sheet(tmp_path, cols=4, rows=3,
                                          frame_w=32, frame_h=32)
    sheet = SpriteSheet(sheet_path)
    assert sheet.frame_width > 0
    assert sheet.frame_height > 0
