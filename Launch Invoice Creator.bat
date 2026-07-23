@echo off
setlocal EnableExtensions

title Invoice Creator

python -m invoice_creator
set "EXIT_CODE=%errorlevel%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo ==========================================
    echo Invoice Creator could not be started.
    echo ==========================================
    echo.
    echo Confirm that:
    echo   1. Python is available on PATH.
    echo   2. Invoice Creator is installed.
    echo   3. Streamlit is installed in the same Python environment.
    echo.
    pause
)

exit /b %EXIT_CODE%
