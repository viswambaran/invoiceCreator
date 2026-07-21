from __future__ import annotations

import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import bootstrap


APP_NAME = "Invoice Creator"
DEFAULT_PORT = 8501


def resource_path(relative_path: str) -> Path:
    """Return a bundled resource path for normal and PyInstaller execution."""
    bundle_root = Path(
        getattr(
            sys,
            "_MEIPASS",
            Path(__file__).resolve().parent.parent,
        )
    )
    return bundle_root / relative_path


def port_is_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except OSError:
        return False


def find_available_port(start_port: int = DEFAULT_PORT) -> int:
    for port in range(start_port, start_port + 50):
        if not port_is_open("127.0.0.1", port):
            return port
    raise RuntimeError("No available local port was found.")


def open_browser_when_ready(port: int) -> None:
    url = f"http://127.0.0.1:{port}"

    for _ in range(120):
        if port_is_open("127.0.0.1", port):
            webbrowser.open(url)
            return
        time.sleep(0.25)


def main() -> None:
    app_path = resource_path("streamlit_app.py")

    if not app_path.is_file():
        raise FileNotFoundError(
            f"{APP_NAME} could not find its application file: {app_path}"
        )

    port = find_available_port()

    threading.Thread(
        target=open_browser_when_ready,
        args=(port,),
        daemon=True,
    ).start()

    flag_options = {
        "server.headless": True,
        "server.address": "127.0.0.1",
        "server.port": port,
        "browser.gatherUsageStats": False,
        "global.developmentMode": False,
    }

    bootstrap.run(
        str(app_path),
        False,
        [],
        flag_options,
    )


if __name__ == "__main__":
    main()
