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
    app = (
        Path(__file__).resolve().parent.parent
        / "__main__.py"
    )

    threading.Thread(
        target=open_browser,
        daemon=True,
    ).start()

    bootstrap.run(
        str(app),
        "",
        [],
        {},
    )


if __name__ == "__main__":
    main()