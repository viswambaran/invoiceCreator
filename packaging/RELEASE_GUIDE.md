# Invoice Creator — Windows Build

## Files to copy into the project

Copy the entire `packaging` folder into the project root:

```text
invoiceCreator/
├── invoice_creator/
├── templates/
├── streamlit_app.py
└── packaging/
    ├── build.py
    ├── desktop_launcher.py
    ├── invoice_creator.spec
    ├── InvoiceCreator.iss
    └── RELEASE_GUIDE.md
```

## Install the build dependency

From the project root:

```powershell
uv add --dev pyinstaller
```

## Build the Windows application

```powershell
uv run python packaging\build.py
```

The application will be created at:

```text
dist\Invoice Creator\Invoice Creator.exe
```

Test the executable directly before creating an installer.

## Build the installer

Install Inno Setup 6, then run:

```powershell
uv run python packaging\build.py --installer
```

The installer will be written under:

```text
dist\installer\
```

## Important

This is a one-folder PyInstaller build. Distribute the complete
`dist\Invoice Creator` folder, not only the `.exe`.

The PDF engine is not modified by these packaging files.
