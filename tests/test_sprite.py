import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QColor

app = QApplication.instance() or QApplication(sys.argv)


def create_test_frames(path: Path, count: int = 3) -> list[str]:
    colors = [QColor(255, 0, 0), QColor(0, 255, 0), QColor(0, 0, 255)]
    names = []
    for i in range(count):
        img = QImage(32, 32, QImage.Format.Format_ARGB32)
        img.fill(colors[i % len(colors)])
        name = f"test_frame_{i+1:02d}.png"
        img.save(str(path / name))
        names.append(name)
    return names


def test_load_frames(tmp_path):
    from watchingai.sprite import FrameLoader
    names = create_test_frames(tmp_path)
    loader = FrameLoader(frames_dir=tmp_path)
    frames = loader.load_frames(names)
    assert len(frames) == 3
    for f in frames:
        assert f.width() == 32
        assert f.height() == 32


def test_load_frames_skips_missing(tmp_path):
    from watchingai.sprite import FrameLoader
    names = create_test_frames(tmp_path, count=2)
    loader = FrameLoader(frames_dir=tmp_path)
    frames = loader.load_frames(names + ["nonexistent.png"])
    assert len(frames) == 2


def test_load_from_assets_fallback(tmp_path):
    from watchingai.sprite import FrameLoader
    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    names = create_test_frames(assets_dir, count=2)
    loader = FrameLoader(frames_dir=frames_dir, assets_dir=assets_dir)
    frames = loader.load_frames(names)
    assert len(frames) == 2


def test_list_available_frames(tmp_path):
    from watchingai.sprite import FrameLoader
    create_test_frames(tmp_path, count=3)
    loader = FrameLoader(frames_dir=tmp_path)
    available = loader.list_available_frames()
    assert len(available) == 3
    assert all(name.endswith(".png") for name in available)


def test_empty_frames_dir(tmp_path):
    from watchingai.sprite import FrameLoader
    loader = FrameLoader(frames_dir=tmp_path)
    frames = loader.load_frames([])
    assert len(frames) == 0
