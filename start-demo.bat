@echo off
REM =============================================================
REM start-demo.bat — One-command classroom launcher (Windows)
REM
REM What this does:
REM   1. Activates the Python virtual environment
REM   2. Generates TLS certificate if missing
REM   3. Starts HTTPS demo server (port 5443) with TLS key logging
REM   4. Starts HTTP  demo server (port 5000)
REM   5. Launches Chrome with --ssl-key-log-file for HTTPS decryption
REM   6. Prints exact Wireshark configuration steps
REM
REM Usage:  Double-click start-demo.bat  OR  run from Command Prompt
REM =============================================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

set HTTPS_PORT=5443
set HTTP_PORT=5000
set KEYLOG_FILE=%~dp0tlskeys\sslkeys.log

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║     Security Awareness Demo — HTTPS Decryption Lab          ║
echo ║              Local lab — educational use only               ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM ── 1. Ensure venv and deps ──────────────────────────────────────────
echo [1/6] Setting up virtual environment ...
where uv >nul 2>&1
if %ERRORLEVEL% == 0 (
    uv sync --no-dev -q
    set PYTHON=.venv\Scripts\python.exe
    echo     OK: uv sync complete
) else (
    if exist ".venv\Scripts\python.exe" (
        set PYTHON=.venv\Scripts\python.exe
        echo     OK: existing venv found
    ) else (
        python -m venv .venv
        .venv\Scripts\pip install -r requirements.txt -q
        set PYTHON=.venv\Scripts\python.exe
        echo     OK: venv created with pip
    )
)

REM ── 2. Generate TLS certificate if missing ───────────────────────────
echo [2/6] Checking TLS certificate ...
if not exist "certs\cert.pem" (
    %PYTHON% scripts\generate_cert.py
    echo     OK: certificate generated
) else (
    echo     OK: certificate already present
)

REM ── 3. Ensure TLS key log file exists ────────────────────────────────
echo [3/6] Setting up TLS key log ...
if not exist "tlskeys" mkdir tlskeys
if not exist "%KEYLOG_FILE%" type nul > "%KEYLOG_FILE%"
echo     OK: key log ready: %KEYLOG_FILE%

REM ── 4. Start HTTPS server ─────────────────────────────────────────────
echo [4/6] Starting HTTPS server (port %HTTPS_PORT%) ...
start "HTTPS Server" /MIN %PYTHON% scripts\start_https.py
echo     OK: HTTPS server starting

REM ── 5. Start HTTP server ──────────────────────────────────────────────
echo [5/6] Starting HTTP server (port %HTTP_PORT%) ...
start "HTTP Server"  /MIN %PYTHON% scripts\start_http.py
echo     OK: HTTP server starting

REM ── Wait for servers to bind ──────────────────────────────────────────
timeout /t 2 /nobreak > nul

REM ── 6. Launch Chrome with SSL key logging ─────────────────────────────
echo [6/6] Launching Chrome with SSL key logging ...
%PYTHON% scripts\launch_browser.py "https://127.0.0.1:%HTTPS_PORT%/"
echo     OK: Chrome launched

REM ── Print Wireshark configuration ─────────────────────────────────────
echo.
echo ════════════════════════════════════════════════════════════════
echo   WIRESHARK SETUP — Step by Step
echo ════════════════════════════════════════════════════════════════
echo.
echo   Step 1  Open Wireshark
echo           Select interface: Loopback Adapter (requires Npcap)
echo           Download Npcap: https://npcap.com/
echo.
echo   Step 2  Configure TLS decryption:
echo           Wireshark -^> Preferences -^> Protocols -^> TLS
echo           (Pre)-Master-Secret log filename:
echo           %KEYLOG_FILE%
echo.
echo   Step 3  Start capture — apply display filter:
echo           tcp.port == %HTTPS_PORT%
echo.
echo   Step 4  In Chrome, go to:
echo           https://127.0.0.1:%HTTPS_PORT%/auth/login
echo           Submit any demo credentials
echo.
echo   Step 5  In Wireshark, switch filter to:
echo           http2
echo           You will see the DECRYPTED HTTP/2 POST with credentials!
echo.
echo ════════════════════════════════════════════════════════════════
echo.
echo   Display filters:
echo     tls                              - all TLS records
echo     http2                            - decrypted HTTP/2 frames
echo     tcp.port == %HTTPS_PORT%                - HTTPS traffic
echo     http.request.method == "POST"    - login/form submissions
echo.
echo   TLS key log: %KEYLOG_FILE%
echo.
echo   Close this window or press Ctrl+C to stop servers.
echo.
pause
