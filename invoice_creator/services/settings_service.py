from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from invoice_creator.services.app_paths import settings_path

LOGGER = logging.getLogger(__name__)

PERSISTED_KEYS = {
    "output_mode",
    "output_folder",
    "create_timestamped_folder",
    "overwrite_existing_pdfs",
    "open_folder_when_finished",
}


def load_settings() -> dict[str, Any]:
    path = settings_path()
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        LOGGER.exception("Unable to read settings from %s", path)
        return {}

    if not isinstance(data, dict):
        return {}

    return {key: value for key, value in data.items() if key in PERSISTED_KEYS}


def save_settings(values: dict[str, Any]) -> None:
    path = settings_path()
    filtered = {key: values[key] for key in PERSISTED_KEYS if key in values}

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = Path(f"{path}.tmp")
        temporary_path.write_text(
            json.dumps(filtered, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        temporary_path.replace(path)
    except OSError:
        LOGGER.exception("Unable to save settings to %s", path)
