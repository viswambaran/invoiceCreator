# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules


# PyInstaller supplies SPECPATH as the directory containing this spec file.
# In this project that directory is:
#   <project root>\packaging
SPEC_DIR = Path(SPECPATH).resolve()
PROJECT_ROOT = SPEC_DIR.parent

LAUNCHER = SPEC_DIR / "desktop_launcher.py"
APP_ENTRY = PROJECT_ROOT / "streamlit_app.py"
TEMPLATES = PROJECT_ROOT / "templates"

streamlit_datas, streamlit_binaries, streamlit_hidden = collect_all(
    "streamlit"
)
pymupdf_datas, pymupdf_binaries, pymupdf_hidden = collect_all(
    "fitz"
)

hiddenimports = sorted(
    set(
        streamlit_hidden
        + pymupdf_hidden
        + collect_submodules("openpyxl")
        + [
            "pandas",
            "pandas._libs.tslibs.base",
            "pandas._libs.tslibs.np_datetime",
            "pandas._libs.tslibs.nattype",
            "pandas._libs.tslibs.timezones",
            "invoice_creator",
            "invoice_creator.app",
        ]
    )
)

datas = [
    (str(APP_ENTRY), "."),
    (str(TEMPLATES), "templates"),
] + streamlit_datas + pymupdf_datas

binaries = streamlit_binaries + pymupdf_binaries

a = Analysis(
    [str(LAUNCHER)],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "pandas.tests",
        "numpy.tests",
        "IPython",
        "jupyter",
        "notebook",
        "tkinter",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Invoice Creator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="Invoice Creator",
)
