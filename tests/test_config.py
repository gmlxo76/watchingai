import json
from pathlib import Path


def test_default_config_created(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    assert config.position_preset == "bottom-right"
    assert config.sprite_sheet == "default_sprite.png"
    assert config.frame_width == 64
    assert config.frame_height == 64
    assert config.size == 64
    assert config.poll_interval_ms == 1500
    assert "idle" in config.animations
    assert "working" in config.animations
    assert "thinking" in config.animations
    assert "done" in config.animations
    assert "error" in config.animations


def test_config_saves_and_loads(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    config.position_preset = "top-left"
    config.size = 128
    config.save()

    config2 = Config(config_dir=tmp_path)
    assert config2.position_preset == "top-left"
    assert config2.size == 128


def test_config_custom_position(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    config.custom_position = (100, 200)
    config.save()

    config2 = Config(config_dir=tmp_path)
    assert config2.custom_position == (100, 200)


def test_config_animation_mapping(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    config.animations["idle"] = {"row": 9, "columns": [1, 2, 3, 4]}
    config.save()

    config2 = Config(config_dir=tmp_path)
    assert config2.animations["idle"]["row"] == 9
    assert config2.animations["idle"]["columns"] == [1, 2, 3, 4]


def test_config_corrupt_file_resets_to_default(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("not valid json{{{")

    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    assert config.position_preset == "bottom-right"
