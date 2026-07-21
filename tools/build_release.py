from pathlib import Path
import shutil
import subprocess
import re

ROOT = Path(__file__).resolve().parents[1]

DIST = ROOT / "dist"
RELEASE = ROOT / "release"

print("Building wheel...")
subprocess.run(["uv", "build"], check=True)

wheel = sorted(DIST.glob("invoicecreator-*.whl"))[-1]

match = re.search(r"invoicecreator-(.+?)-", wheel.name)
version = match.group(1)

release_dir = RELEASE / f"InvoiceCreator-v{version}"

if release_dir.exists():
    shutil.rmtree(release_dir)

release_dir.mkdir(parents=True)

shutil.copy2(wheel, release_dir / wheel.name)
shutil.copy2(ROOT / "Install Invoice Creator.bat",
             release_dir / "Install Invoice Creator.bat")
shutil.copy2(ROOT / "README.txt",
             release_dir / "README.txt")

zip_name = RELEASE / f"InvoiceCreator-v{version}"

if zip_name.with_suffix(".zip").exists():
    zip_name.with_suffix(".zip").unlink()

shutil.make_archive(str(zip_name), "zip", release_dir)

print()
print("Release created:")
print(zip_name.with_suffix(".zip"))