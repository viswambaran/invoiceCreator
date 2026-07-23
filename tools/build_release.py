from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASE = ROOT / "release"

REQUIRED_RELEASE_FILES = (
    "Install Invoice Creator.bat",
    "Launch Invoice Creator.bat",
    "README.txt",
)


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Invoice Creator wheel and release ZIP."
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Create a GitHub release using the GitHub CLI after building.",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create the GitHub release as a draft. Requires --github.",
    )
    return parser.parse_args()


def require_source_files() -> None:
    missing = [
        filename
        for filename in REQUIRED_RELEASE_FILES
        if not (ROOT / filename).is_file()
    ]
    if missing:
        formatted = "\n".join(f"  - {name}" for name in missing)
        raise FileNotFoundError(
            "The following release files are missing:\n"
            f"{formatted}"
        )


def clean_build_directories() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)

    DIST.mkdir(parents=True, exist_ok=True)
    RELEASE.mkdir(parents=True, exist_ok=True)


def build_wheel() -> Path:
    print("Building wheel...")
    run(["uv", "build", "--wheel"])

    wheels = sorted(DIST.glob("invoicecreator-*.whl"))
    if len(wheels) != 1:
        names = ", ".join(wheel.name for wheel in wheels) or "none"
        raise RuntimeError(
            "Expected exactly one invoicecreator wheel in dist, "
            f"but found: {names}"
        )

    return wheels[0]


def version_from_wheel(wheel: Path) -> str:
    match = re.fullmatch(
        r"invoicecreator-(?P<version>.+?)-[^-]+-[^-]+-[^-]+\.whl",
        wheel.name,
    )
    if not match:
        raise RuntimeError(
            f"Could not determine the version from wheel name: {wheel.name}"
        )

    return match.group("version")


def create_release_directory(wheel: Path, version: str) -> tuple[Path, Path]:
    release_dir = RELEASE / f"InvoiceCreator-v{version}"
    zip_path = RELEASE / f"InvoiceCreator-v{version}.zip"

    if release_dir.exists():
        shutil.rmtree(release_dir)

    if zip_path.exists():
        zip_path.unlink()

    release_dir.mkdir(parents=True)

    shutil.copy2(wheel, release_dir / wheel.name)

    for filename in REQUIRED_RELEASE_FILES:
        shutil.copy2(ROOT / filename, release_dir / filename)

    archive_base = zip_path.with_suffix("")
    created_zip = Path(
        shutil.make_archive(
            str(archive_base),
            "zip",
            root_dir=release_dir.parent,
            base_dir=release_dir.name,
        )
    )

    return release_dir, created_zip


def create_github_release(
    *,
    version: str,
    zip_path: Path,
    wheel: Path,
    draft: bool,
) -> None:
    if shutil.which("gh") is None:
        raise RuntimeError(
            "The GitHub CLI command 'gh' was not found. "
            "Install it or run without --github."
        )

    tag = f"v{version}"
    command = [
        "gh",
        "release",
        "create",
        tag,
        str(zip_path),
        str(wheel),
        "--title",
        f"Invoice Creator {tag}",
        "--generate-notes",
    ]

    if draft:
        command.append("--draft")

    run(command)


def main() -> int:
    args = parse_args()

    if args.draft and not args.github:
        raise SystemExit("--draft can only be used together with --github.")

    require_source_files()
    clean_build_directories()

    wheel = build_wheel()
    version = version_from_wheel(wheel)
    release_dir, zip_path = create_release_directory(wheel, version)

    print()
    print("Release created:")
    print(f"  Folder: {release_dir}")
    print(f"  ZIP:    {zip_path}")

    if args.github:
        print()
        print("Creating GitHub release...")
        create_github_release(
            version=version,
            zip_path=zip_path,
            wheel=wheel,
            draft=args.draft,
        )
        print(f"GitHub release v{version} created.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(
            f"\nCommand failed with exit code {exc.returncode}.",
            file=sys.stderr,
        )
        raise SystemExit(exc.returncode) from exc
    except Exception as exc:
        print(f"\nRelease build failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
