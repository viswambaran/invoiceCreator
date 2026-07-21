from __future__ import annotations

import os
import sys
from pathlib import Path

from invoice_creator.app_info import APP_NAME


def user_data_directory() -> Path:
    """Return a writable, per-user application-data directory."""
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    return base / APP_NAME


def settings_path() -> Path:
    return user_data_directory() / "settings.json"


def logs_directory() -> Path:
    return user_data_directory() / "logs"


def default_output_directory() -> Path:
    home = Path.home()
    documents = home / "Documents"
    base = documents if documents.exists() else home
    return base / APP_NAME / "Generated Invoices"
