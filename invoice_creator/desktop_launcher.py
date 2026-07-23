from __future__ import annotations

import subprocess
import sys
from importlib.resources import as_file, files


def main() -> None:
    app_resource = files("invoice_creator").joinpath("app.py")

    with as_file(app_resource) as app_path:
        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ]

        try:
            subprocess.run(
                command,
                check=True,
            )
        except KeyboardInterrupt:
            pass
        except subprocess.CalledProcessError as exc:
            raise SystemExit(
                f"Invoice Creator failed to start: {exc}"
            ) from exc


if __name__ == "__main__":
    main()