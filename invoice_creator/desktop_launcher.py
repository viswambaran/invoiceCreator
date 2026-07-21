from __future__ import annotations

import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import bootstrap


def open_browser() -> None:
    time.sleep(2)
    webbrowser.open("http://localhost:8501")


def main() -> None:
    app = Path(__file__).resolve().parent / "__main__.py"

    if not app.exists():
        raise FileNotFoundError(
            f"Invoice Creator entry file was not found: {app}"
        )

    threading.Thread(
        target=open_browser,
        daemon=True,
    ).start()

    bootstrap.run(
        str(app),
        False,
        [],
        {
            "server.port": 8501,
            "server.headless": True,
        },
    )


if __name__ == "__main__":
    main()