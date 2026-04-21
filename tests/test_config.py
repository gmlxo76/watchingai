from pathlib import Path


def test_default_config_created(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    assert config.position_preset == "bottom-right"
    assert config.size == 128
    assert config.poll_interval_ms == 1500
    assert isinstance(config.animations["idle"], list)
    assert isinstance(config.animations["working"], list)
    assert isinstance(config.animations["thinking"], list)
    assert isinstance(config.animations["done"], list)
    assert isinstance(config.animations["error"], list)


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


def test_config_animation_frame_list(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    config.animations["idle"] = ["frame_01.png", "frame_02.png"]
    config.save()

    config2 = Config(config_dir=tmp_path)
    assert config2.animations["idle"] == ["frame_01.png", "frame_02.png"]


def test_config_corrupt_file_resets_to_default(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("not valid json{{{")

    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    assert config.position_preset == "bottom-right"


def test_frames_dir(tmp_path):
    from watchingai.config import Config
    config = Config(config_dir=tmp_path)
    assert config.frames_dir == tmp_path / "frames"
