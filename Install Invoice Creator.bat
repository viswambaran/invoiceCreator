@echo off
setlocal EnableExtensions EnableDelayedExpansion

title Invoice Creator Installer

echo.
echo ==========================================
echo      Invoice Creator Installer
echo ==========================================
echo.

rem Run from the folder containing this installer.
cd /d "%~dp0"

rem Confirm Python is available.
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or is not available on PATH.
    echo.
    echo Please install Python 3.10 or newer, then run this installer again.
    pause
    exit /b 1
)

rem Find the wheel included in this release.
set "WHEEL="
for %%F in (invoicecreator-*.whl) do (
    set "WHEEL=%%~fF"
)

if not defined WHEEL (
    echo ERROR: No invoicecreator wheel was found beside this installer.
    pause
    exit /b 1
)

echo Installing:
echo   %WHEEL%
echo.

python -m pip install --upgrade "%WHEEL%"
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed.
    pause
    exit /b 1
)

rem Store a stable launcher outside site-packages.
set "APP_DIR=%LOCALAPPDATA%\InvoiceCreator"
set "LAUNCHER=%APP_DIR%\Launch Invoice Creator.bat"

if not exist "%APP_DIR%" mkdir "%APP_DIR%"

copy /Y "%~dp0Launch Invoice Creator.bat" "%LAUNCHER%" >nul
if errorlevel 1 (
    echo.
    echo ERROR: Could not install the launcher.
    pause
    exit /b 1
)

echo.
echo Creating shortcuts...
echo.

rem The shortcut targets cmd.exe, not invoicecreator.exe or streamlit.exe.
rem PowerShell is used only to create the .lnk files.
set "SHORTCUT_OK=1"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$shell=New-Object -ComObject WScript.Shell;" ^
  "$desktop=[Environment]::GetFolderPath('Desktop');" ^
  "$programs=[Environment]::GetFolderPath('Programs');" ^
  "$target=$env:ComSpec;" ^
  "$launcher=$env:LAUNCHER;" ^
  "$args='/c """"'+$launcher+'""""';" ^
  "$s=$shell.CreateShortcut((Join-Path $desktop 'Invoice Creator.lnk'));" ^
  "$s.TargetPath=$target;" ^
  "$s.Arguments=$args;" ^
  "$s.WorkingDirectory=$env:USERPROFILE;" ^
  "$s.Save();" ^
  "$s=$shell.CreateShortcut((Join-Path $programs 'Invoice Creator.lnk'));" ^
  "$s.TargetPath=$target;" ^
  "$s.Arguments=$args;" ^
  "$s.WorkingDirectory=$env:USERPROFILE;" ^
  "$s.Save();" >nul 2>&1

if errorlevel 1 set "SHORTCUT_OK=0"

if "%SHORTCUT_OK%"=="0" (
    echo Shortcut creation was blocked.
    echo Creating ordinary batch launchers instead...

    copy /Y "%LAUNCHER%" "%USERPROFILE%\Desktop\Invoice Creator.bat" >nul 2>&1

    set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
    if exist "%START_MENU%" (
        copy /Y "%LAUNCHER%" "%START_MENU%\Invoice Creator.bat" >nul 2>&1
    )

    echo.
    echo A launcher has been placed on the Desktop where permitted.
) else (
    echo Desktop and Start Menu shortcuts created.
)

echo.
echo ==========================================
echo Installation Complete
echo ==========================================
echo.
echo Invoice Creator will now start.
echo.

call "%LAUNCHER%"

exit /b %errorlevel%
