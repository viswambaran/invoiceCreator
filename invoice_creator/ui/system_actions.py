from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def open_directory(path: Path) -> None:
    resolved = path.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)

    if sys.platform.startswith("win"):
        os.startfile(str(resolved))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(resolved)])
    else:
        subprocess.Popen(["xdg-open", str(resolved)])
