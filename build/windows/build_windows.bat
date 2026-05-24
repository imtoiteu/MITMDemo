@echo off
REM ============================================================
REM build_windows.bat — Build AwarenessDemo.exe with PyInstaller
REM
REM Prerequisites:
REM   1. Python 3.10+ installed and on PATH
REM   2. uv installed  (winget install astral-sh.uv)
REM   3. Run from the project root:
REM        build\windows\build_windows.bat
REM ============================================================

echo.
echo [build] Installing PyInstaller ...
uv add --dev pyinstaller
if %ERRORLEVEL% neq 0 (
    echo [build] ERROR: Failed to install PyInstaller.
    exit /b 1
)

echo.
echo [build] Generating TLS certificate (if missing) ...
uv run python scripts\generate_cert.py

echo.
echo [build] Running PyInstaller ...
uv run pyinstaller build\awareness_demo.spec --distpath dist --workpath build\work --clean

if %ERRORLEVEL% neq 0 (
    echo [build] ERROR: PyInstaller build failed.
    exit /b 1
)

echo.
echo [build] SUCCESS!
echo [build] Output: dist\AwarenessDemo.exe
echo [build] Double-click AwarenessDemo.exe to run the demo.
echo.
pause
