import json
from pathlib import Path

DEFAULT_ANIMATIONS = {
    "idle": ["frame_01.png", "frame_02.png", "frame_03.png", "frame_04.png"],
    "thinking": ["frame_06.png", "frame_07.png", "frame_08.png", "frame_09.png", "frame_10.png"],
    "working": ["frame_11.png", "frame_14.png"],
    "done": ["frame_01.png", "frame_02.png", "frame_03.png", "frame_04.png", "frame_05.png"],
    "error": ["frame_01.png", "frame_02.png", "frame_03.png", "frame_04.png", "frame_05.png"],
}

DEFAULT_CONFIG = {
    "position": {
        "preset": "bottom-right",
        "custom": None,
    },
    "animations": DEFAULT_ANIMATIONS,
    "size_ratio": 0.5,
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
        return self._data.get("size", 128)

    @size.setter
    def size(self, value: int) -> None:
        self._data["size"] = value

    @property
    def size_ratio(self) -> float:
        return self._data.get("size_ratio", 1.0)

    @size_ratio.setter
    def size_ratio(self, value: float) -> None:
        self._data["size_ratio"] = value

    @property
    def poll_interval_ms(self) -> int:
        return self._data["poll_interval_ms"]

    @property
    def config_dir(self) -> Path:
        return self._config_dir

    @property
    def frames_dir(self) -> Path:
        return self._config_dir / "frames"
