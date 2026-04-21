import json
from pathlib import Path

DEFAULT_ANIMATIONS = {
    "idle": ["frame_29.png", "frame_30.png", "frame_31.png", "frame_32.png"],
    "thinking": ["frame_09.png", "frame_10.png", "frame_11.png", "frame_12.png"],
    "working": ["frame_13.png", "frame_14.png", "frame_15.png", "frame_16.png"],
    "done": ["frame_17.png", "frame_18.png", "frame_19.png", "frame_20.png"],
    "error": ["frame_25.png", "frame_26.png", "frame_27.png", "frame_28.png"],
}

DEFAULT_CONFIG = {
    "position": {
        "preset": "bottom-right",
        "custom": None,
    },
    "animations": DEFAULT_ANIMATIONS,
    "size": 128,
    "poll_interval_ms": 1500,
}


class Config:
    def __init__(self, config_dir: Path | None = None):
        if config_dir is None:
            config_dir = Path.home() / ".watchingai"
        self._config_dir = config_dir
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._config_file = self._config_dir / "config.json"
        self._data = self._load()

    def _load(self) -> dict:
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        data = json.loads(json.dumps(DEFAULT_CONFIG))
        self._save_data(data)
        return data

    def _save_data(self, data: dict) -> None:
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self) -> None:
        self._save_data(self._data)

    @property
    def position_preset(self) -> str:
        return self._data["position"]["preset"]

    @position_preset.setter
    def position_preset(self, value: str) -> None:
        self._data["position"]["preset"] = value

    @property
    def custom_position(self) -> tuple[int, int] | None:
        val = self._data["position"]["custom"]
        if val is not None:
            return tuple(val)
        return None

    @custom_position.setter
    def custom_position(self, value: tuple[int, int] | None) -> None:
        self._data["position"]["custom"] = list(value) if value else None

    @property
    def animations(self) -> dict:
        return self._data["animations"]

    @property
    def size(self) -> int:
        return self._data["size"]

    @size.setter
    def size(self, value: int) -> None:
        self._data["size"] = value

    @property
    def poll_interval_ms(self) -> int:
        return self._data["poll_interval_ms"]

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def frames_dir(self) -> Path:
        return self._config_dir / "frames"
