import json
from pathlib import Path

DEFAULT_ANIMATIONS = {
    "idle": {"row": 9, "columns": [1, 2, 3, 4]},
    "thinking": {"row": 3, "columns": [1, 2, 3, 4]},
    "working": {"row": 4, "columns": [1, 2, 3, 4]},
    "done": {"row": 5, "columns": [1, 2, 3, 4]},
    "error": {"row": 7, "columns": [1, 2, 3, 4]},
}

DEFAULT_CONFIG = {
    "position": {
        "preset": "bottom-right",
        "custom": None,
    },
    "sprite": {
        "sheet": "default_sprite.png",
        "rows": 9,
        "cols": 4,
        "animations": DEFAULT_ANIMATIONS,
    },
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
    def sprite_sheet(self) -> str:
        return self._data["sprite"]["sheet"]

    @sprite_sheet.setter
    def sprite_sheet(self, value: str) -> None:
        self._data["sprite"]["sheet"] = value

    @property
    def sprite_rows(self) -> int:
        return self._data["sprite"].get("rows", 0)

    @property
    def sprite_cols(self) -> int:
        return self._data["sprite"].get("cols", 0)

    @property
    def animations(self) -> dict:
        return self._data["sprite"]["animations"]

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
