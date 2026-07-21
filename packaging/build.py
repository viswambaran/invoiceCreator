from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGING_DIR = PROJECT_ROOT / "packaging"
SPEC_FILE = PACKAGING_DIR / "invoice_creator.spec"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
APP_DIST_DIR = DIST_DIR / "Invoice Creator"


REQUIRED_PATHS = [
    PROJECT_ROOT / "streamlit_app.py",
    PROJECT_ROOT / "invoice_creator",
    PROJECT_ROOT / "templates",
    PACKAGING_DIR / "desktop_launcher.py",
    SPEC_FILE,
]


def heading(message: str) -> None:
    print()
    print("=" * 72)
    print(message)
    print("=" * 72)


def check_environment() -> None:
    heading("Checking build environment")

    if os.name != "nt":
        raise RuntimeError("This build system supports Windows only.")

    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer is required.")

    missing = [path for path in REQUIRED_PATHS if not path.exists()]
    if missing:
        formatted = "\n".join(f"  - {path}" for path in missing)
        raise FileNotFoundError(
            "Required project files are missing:\n" + formatted
        )

    try:
        import PyInstaller  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "PyInstaller is not installed. Run:\n"
            "  uv add --dev pyinstaller"
        ) from exc

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Python:       {sys.executable}")
    print(f"Version:      {sys.version.split()[0]}")
    print("Environment checks passed.")


def clean() -> None:
    heading("Cleaning previous output")

    for path in (BUILD_DIR, APP_DIST_DIR):
        if path.exists():
            print(f"Removing {path}")
            shutil.rmtree(path)

    print("Clean complete.")


def run_pyinstaller() -> None:
    heading("Building Invoice Creator")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        str(SPEC_FILE),
    ]

    print("Running:")
    print(" ".join(f'"{part}"' if " " in part else part for part in command))

    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
    )


def verify_output() -> Path:
    heading("Verifying build")

    executable = APP_DIST_DIR / "Invoice Creator.exe"

    if not executable.is_file():
        raise FileNotFoundError(
            f"Build completed but the executable was not found:\n{executable}"
        )

    streamlit_entry = APP_DIST_DIR / "_internal" / "streamlit_app.py"
    if not streamlit_entry.exists():
        # PyInstaller layouts can vary slightly; this is informational only.
        print(
            "Warning: streamlit_app.py was not found at the usual "
            "_internal location. The executable will still be tested manually."
        )

    size_mb = executable.stat().st_size / (1024 * 1024)
    print(f"Executable: {executable}")
    print(f"Launcher size: {size_mb:.2f} MB")
    print("Build verification passed.")

    return executable


def find_inno_setup() -> Path | None:
    candidates = [
        Path(os.environ.get("ProgramFiles(x86)", ""))
        / "Inno Setup 6"
        / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", ""))
        / "Inno Setup 6"
        / "ISCC.exe",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None


def build_installer() -> None:
    heading("Building Windows installer")

    iscc = find_inno_setup()
    if iscc is None:
        raise FileNotFoundError(
            "Inno Setup 6 was not found. Install it, then rerun with "
            "--installer."
        )

    script = PACKAGING_DIR / "InvoiceCreator.iss"
    if not script.is_file():
        raise FileNotFoundError(f"Installer script not found: {script}")

    subprocess.run(
        [str(iscc), str(script)],
        cwd=PROJECT_ROOT,
        check=True,
    )

    print("Installer build complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Windows Invoice Creator application."
    )
    parser.add_argument(
        "--installer",
        action="store_true",
        help="Also build the Inno Setup installer.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not delete previous build output first.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        check_environment()

        if not args.no_clean:
            clean()

        run_pyinstaller()
        executable = verify_output()

        if args.installer:
            build_installer()

        heading("Build successful")
        print(f"Test this file:\n  {executable}")
        return 0

    except subprocess.CalledProcessError as exc:
        heading("Build failed")
        print(f"A build command exited with status {exc.returncode}.")
        return exc.returncode or 1

    except Exception as exc:
        heading("Build failed")
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
