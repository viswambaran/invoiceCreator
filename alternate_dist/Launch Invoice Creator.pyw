from __future__ import annotations

import importlib.util
import logging
import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from tkinter import messagebox

APP_PORT = 8501
APP_URL = f"http://127.0.0.1:{APP_PORT}"
ROOT = Path(__file__).resolve().parent


def _launcher_log_path() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".invoice_creator"
    path = base / "Invoice Creator" / "logs" / "launcher.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


logging.basicConfig(
    filename=_launcher_log_path(),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def _port_is_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex(("127.0.0.1", APP_PORT)) == 0


def _hidden_creation_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _ensure_dependencies() -> None:
    required_modules = ("streamlit", "pandas", "openpyxl", "fitz", "numpy")
    missing = [name for name in required_modules if importlib.util.find_spec(name) is None]
    if not missing:
        return

    requirements = ROOT / "requirements.txt"
    if not requirements.exists():
        raise FileNotFoundError("requirements.txt is missing from the application folder.")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "-r",
            str(requirements),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        creationflags=_hidden_creation_flags(),
    )
    if result.returncode != 0:
        logging.error("Dependency installation failed: %s", result.stderr)
        raise RuntimeError(
            "Invoice Creator could not install its required Python packages. "
            "Your organisation may block package installation or internet access."
        )


def main() -> None:
    try:
        if _port_is_open():
            webbrowser.open(APP_URL)
            return

        _ensure_dependencies()

        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(ROOT / "streamlit_app.py"),
            "--server.headless=true",
            f"--server.port={APP_PORT}",
            "--browser.gatherUsageStats=false",
            "--server.fileWatcherType=none",
        ]

        subprocess.Popen(
            command,
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=_hidden_creation_flags(),
        )

        for _ in range(120):
            if _port_is_open():
                webbrowser.open(APP_URL)
                return
            time.sleep(0.25)

        raise RuntimeError("Invoice Creator did not start within 30 seconds.")
    except Exception as exc:
        logging.exception("Launcher failed")
        messagebox.showerror(
            "Invoice Creator",
            f"Invoice Creator could not start.\n\n{exc}\n\n"
            f"A support log was written to:\n{_launcher_log_path()}",
        )


if __name__ == "__main__":
    main()
