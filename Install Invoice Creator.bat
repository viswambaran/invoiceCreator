@echo off
setlocal EnableDelayedExpansion

title Invoice Creator Installer

echo.
echo ==========================================
echo      Invoice Creator Installer
echo ==========================================
echo.

:: Ensure Python exists
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not on PATH.
    echo Please install Python 3.10 or newer from:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Find wheel
set "WHEEL="

for %%f in (invoicecreator-*.whl) do (
    set "WHEEL=%%f"
)

if "%WHEEL%"=="" (
    echo.
    echo ERROR: No wheel file found.
    pause
    exit /b 1
)

echo Installing %WHEEL%
echo.

python -m pip install --upgrade "%WHEEL%"

if errorlevel 1 (
    echo.
    echo Installation failed.
    pause
    exit /b 1
)

echo.
echo Creating shortcuts...
echo.

powershell -ExecutionPolicy Bypass -NoProfile ^
"$Shell = New-Object -ComObject WScript.Shell;" ^
"$Desktop=[Environment]::GetFolderPath('Desktop');" ^
"$Programs=[Environment]::GetFolderPath('Programs');" ^
"$Target=(Get-Command invoicecreator).Source;" ^
"$Shortcut=$Shell.CreateShortcut($Desktop+'\Invoice Creator.lnk');" ^
"$Shortcut.TargetPath=$Target;" ^
"$Shortcut.WorkingDirectory=$env:USERPROFILE;" ^
"$Shortcut.Save();" ^
"$Shortcut=$Shell.CreateShortcut($Programs+'\Invoice Creator.lnk');" ^
"$Shortcut.TargetPath=$Target;" ^
"$Shortcut.WorkingDirectory=$env:USERPROFILE;" ^
"$Shortcut.Save();"

echo.
echo ==========================================
echo Installation Complete
echo ==========================================
echo.

echo Launching Invoice Creator...
start "" invoicecreator

exit