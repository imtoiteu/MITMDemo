#!/usr/bin/env python3
"""
run.py — One-command launcher for the Security Awareness Demo.

What this script does:
  1. Checks Python version (>=3.10 required)
  2. Creates a virtual environment with uv if missing
  3. Installs all dependencies via uv sync
  4. Generates a self-signed TLS certificate if missing
  5. Creates tlskeys/sslkeys.log for Wireshark TLS decryption
  6. Starts the HTTP server  (port 5000) in a background process
  7. Starts the HTTPS server (port 5443) with TLS session key logging
  8. Launches Chrome with --ssl-key-log-file for HTTPS decryption
  9. Prints Wireshark filters, TLS decryption guide, and demo walkthrough
 10. Blocks until Ctrl+C, then gracefully shuts down both servers

Usage:
    python run.py          # recommended (uses uv)
    python3 run.py         # macOS / Linux alternative

Requirements:
    Python >= 3.10 must be installed and on PATH.
    uv must be installed (https://docs.astral.sh/uv/getting-started/).
"""

import multiprocessing
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
HTTP_PORT = 5000
HTTPS_PORT = 5443
HTTP_URL = f"http://127.0.0.1:{HTTP_PORT}"
HTTPS_URL = f"https://127.0.0.1:{HTTPS_PORT}"
VENV_DIR = PROJECT_ROOT / ".venv"
ON_WINDOWS = platform.system() == "Windows"


# ── Colour helpers (work on both Windows 10+ and Unix) ─────────────────
def _c(code: str, text: str) -> str:
    """Wrap text in an ANSI colour code if the terminal supports it.

    Args:
        code: ANSI escape code string.
        text: Text to colour.

    Returns:
        Coloured text string, or plain text on unsupported terminals.
    """
    if ON_WINDOWS and not os.environ.get("TERM"):
        return text
    return f"\033[{code}m{text}\033[0m"


RED    = lambda t: _c("91", t)   # noqa: E731
GREEN  = lambda t: _c("92", t)   # noqa: E731
YELLOW = lambda t: _c("93", t)   # noqa: E731
CYAN   = lambda t: _c("96", t)   # noqa: E731
BOLD   = lambda t: _c("1",  t)   # noqa: E731
DIM    = lambda t: _c("2",  t)   # noqa: E731


# ── Step helpers ────────────────────────────────────────────────────────
def step(msg: str) -> None:
    """Print a numbered setup step.

    Args:
        msg: Step description.
    """
    print(CYAN(f"\n▶  {msg}"))


def ok(msg: str) -> None:
    """Print a success message.

    Args:
        msg: Success description.
    """
    print(GREEN(f"   ✓  {msg}"))


def warn(msg: str) -> None:
    """Print a warning.

    Args:
        msg: Warning text.
    """
    print(YELLOW(f"   ⚠  {msg}"))


def err(msg: str) -> None:
    """Print an error and exit.

    Args:
        msg: Error text.
    """
    print(RED(f"\n   ✗  {msg}"))
    sys.exit(1)


# ── Environment setup ───────────────────────────────────────────────────
def check_python() -> None:
    """Verify Python version is 3.10 or newer.

    Returns:
        None
    """
    step("Checking Python version …")
    ok(
        f"Python "
        f"{sys.version_info.major}.{sys.version_info.minor}."
        f"{sys.version_info.micro}"
    )


def check_uv() -> bool:
    """Check whether uv is available on PATH.

    Returns:
        True if uv is available, False otherwise.
    """
    try:
        subprocess.run(
            ["uv", "--version"],
            check=True,
            capture_output=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def setup_environment() -> None:
    """Create venv and install dependencies.

    Uses uv if available, falls back to pip.

    Returns:
        None
    """
    step("Setting up virtual environment and dependencies …")

    if check_uv():
        ok("uv detected — using uv for fast install")
        _run_uv_setup()
    else:
        warn(
            "uv not found — falling back to pip. "
            "Install uv for faster setup: "
            "https://docs.astral.sh/uv/"
        )
        _run_pip_setup()


def _run_uv_setup() -> None:
    """Create venv and sync dependencies with uv.

    Returns:
        None
    """
    if not VENV_DIR.exists():
        subprocess.run(
            ["uv", "venv", str(VENV_DIR)],
            cwd=PROJECT_ROOT,
            check=True,
        )
    subprocess.run(
        ["uv", "sync", "--no-dev"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    ok("Dependencies installed via uv")


def _run_pip_setup() -> None:
    """Create venv and install dependencies with pip.

    Returns:
        None
    """
    if not VENV_DIR.exists():
        subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            cwd=PROJECT_ROOT,
            check=True,
        )

    pip = (
        VENV_DIR / "Scripts" / "pip.exe"
        if ON_WINDOWS
        else VENV_DIR / "bin" / "pip"
    )
    subprocess.run(
        [str(pip), "install", "-r", "requirements.txt", "-q"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    ok("Dependencies installed via pip")


def python_in_venv() -> str:
    """Return the path to the Python executable inside the venv.

    Returns:
        Absolute path string to the venv Python.
    """
    if ON_WINDOWS:
        return str(VENV_DIR / "Scripts" / "python.exe")
    return str(VENV_DIR / "bin" / "python")


# ── Certificate ─────────────────────────────────────────────────────────
def ensure_certs() -> None:
    """Generate self-signed TLS certificates if they don't exist.

    Returns:
        None
    """
    step("Checking TLS certificates …")
    cert = PROJECT_ROOT / "certs" / "cert.pem"
    key = PROJECT_ROOT / "certs" / "key.pem"

    if cert.exists() and key.exists():
        ok("Certificates already present — skipping generation")
        return

    py = python_in_venv()
    subprocess.run(
        [py, str(PROJECT_ROOT / "scripts" / "generate_cert.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )
    ok("Self-signed certificate generated")


# ── TLS Key Logging ─────────────────────────────────────────────────────
def ensure_keylog() -> Path:
    """Create the tlskeys directory and empty sslkeys.log if missing.

    The HTTPS server (start_https.py) uses ssl.SSLContext.keylog_filename
    to append NSS key log entries on every TLS handshake.  Wireshark
    can use this file to decrypt HTTPS traffic.

    Returns:
        Absolute path to the sslkeys.log file.
    """
    step("Setting up TLS session key log …")
    keylog = PROJECT_ROOT / "tlskeys" / "sslkeys.log"
    keylog.parent.mkdir(parents=True, exist_ok=True)
    if not keylog.exists():
        keylog.touch()
    ok(f"TLS key log ready → {keylog}")
    return keylog


# ── Chrome launcher ─────────────────────────────────────────────────────
def launch_chrome_with_keylog(keylog: Path, delay: float = 2.0) -> None:
    """Launch Chrome with SSL key logging after a startup delay.

    Args:
        keylog: Path to the sslkeys.log file.
        delay:  Seconds to wait before launching (lets servers bind).

    Returns:
        None
    """
    time.sleep(delay)
    py = python_in_venv()
    launcher = str(PROJECT_ROOT / "scripts" / "launch_browser.py")
    try:
        subprocess.Popen(
            [py, launcher, HTTPS_URL],
            cwd=PROJECT_ROOT,
        )
        print(
            GREEN("   ✓  Chrome launched with SSL key logging")
        )
    except Exception as exc:
        print(YELLOW(f"   ⚠  Chrome auto-launch failed: {exc}"))
        print(
            YELLOW(
                f"      Manually open {HTTPS_URL} in Chrome with:\n"
                f"      --ssl-key-log-file={keylog}"
            )
        )


# ── Server processes ────────────────────────────────────────────────────
def _server_worker(script: str, label: str) -> None:
    """Worker function run in a child process.

    Args:
        script: Path to the start script to run.
        label:  Human-readable label for log messages.
    """
    py = python_in_venv()
    try:
        subprocess.run(
            [py, script],
            cwd=PROJECT_ROOT,
            check=True,
        )
    except KeyboardInterrupt:
        pass
    except subprocess.CalledProcessError as exc:
        print(RED(f"[{label}] Server exited with error: {exc}"))


def start_servers() -> tuple[
    multiprocessing.Process, multiprocessing.Process
]:
    """Start HTTP and HTTPS servers as background processes.

    Returns:
        Tuple of (http_process, https_process).
    """
    step("Starting HTTP server …")
    http_proc = multiprocessing.Process(
        target=_server_worker,
        args=(
            str(PROJECT_ROOT / "scripts" / "start_http.py"),
            "HTTP",
        ),
        daemon=True,
    )
    http_proc.start()
    ok(f"HTTP  server → {HTTP_URL}")

    step("Starting HTTPS server …")
    https_proc = multiprocessing.Process(
        target=_server_worker,
        args=(
            str(PROJECT_ROOT / "scripts" / "start_https.py"),
            "HTTPS",
        ),
        daemon=True,
    )
    https_proc.start()
    ok(f"HTTPS server → {HTTPS_URL}")

    return http_proc, https_proc


# ── Terminal welcome screen ──────────────────────────────────────────────
def print_banner(keylog: Path | None = None) -> None:
    """Print the welcome banner and demo instructions to stdout.

    Args:
        keylog: Optional path to the TLS session key log file.

    Returns:
        None
    """
    width = 70
    line = "─" * width

    print()
    print(BOLD(CYAN("╔" + "═" * width + "╗")))
    print(BOLD(CYAN("║")) + BOLD(
        "  🛡️  SECURITY AWARENESS TRAINING DEMO".center(width)
    ) + BOLD(CYAN("║")))
    print(BOLD(CYAN("║")) + DIM(
        "  Local lab — for educational use only".center(width)
    ) + BOLD(CYAN("║")))
    print(BOLD(CYAN("╚" + "═" * width + "╝")))

    print()
    print(BOLD("  🌐  Demo URLs"))
    print(f"      HTTP  (unencrypted) → {YELLOW(HTTP_URL)}")
    print(f"      HTTPS (TLS)         → {GREEN(HTTPS_URL)}")

    # ── TLS decryption section ───────────────────────────────────────
    if keylog:
        print()
        print(BOLD("  🔓  HTTPS Decryption — Wireshark Setup"))
        print(
            "      TLS session keys are being written to:"
        )
        print(f"      {CYAN(str(keylog))}")
        print()
        print("      To decrypt HTTPS traffic in Wireshark:")
        tls_steps = [
            "Open Wireshark → select loopback interface (lo0 / Loopback)",
            "Edit → Preferences → Protocols → TLS",
            f"(Pre)-Master-Secret log filename → {str(keylog)}",
            "Click OK — Wireshark will now auto-decrypt TLS sessions",
            f"Start capture with filter: tcp.port == {HTTPS_PORT}",
            f"Open {HTTPS_URL}/auth/login in Chrome → submit credentials",
            "Switch Wireshark filter to: http2",
            "You can now read the decrypted POST body with credentials!",
        ]
        for i, s in enumerate(tls_steps, 1):
            print(f"      {DIM(str(i) + '.')} {s}")

    print()
    print(BOLD("  🦈  Wireshark Display Filters"))
    ws = [
        ("All HTTP traffic (plaintext)",
            f"tcp.port == {HTTP_PORT}"),
        ("HTTP POST requests (credentials, forms)",
            f'tcp.port == {HTTP_PORT} && '
            f'http.request.method == "POST"'),
        ("Session cookies",
            "http.cookie"),
        ("All TLS records",
            "tls"),
        ("HTTPS traffic",
            f"tcp.port == {HTTPS_PORT}"),
        ("Decrypted HTTP/2 frames (after loading key log)",
            "http2"),
        ("Decrypted POST requests over HTTPS",
            'http.request.method == "POST"'),
        ("Loopback interface",
            "lo0  (macOS) / Loopback (Windows)"),
    ]
    for label, flt in ws:
        print(f"      {DIM(label)}")
        print(f"        {CYAN(flt)}")

    print()
    print(BOLD("  📋  Demo Walkthrough (HTTP — plaintext)"))
    steps = [
        "Open Wireshark → select loopback interface",
        f"Apply filter:  tcp.port == {HTTP_PORT}",
        f"Open {HTTP_URL}/auth/login  →  submit any credentials",
        "In Wireshark: right-click POST packet → Follow → HTTP Stream",
        "Read username= and password= in PLAINTEXT",
    ]
    for i, s in enumerate(steps, 1):
        print(f"      {DIM(str(i) + '.')} {s}")

    print()
    print(BOLD("  🔓  Demo Walkthrough (HTTPS — decrypted)"))
    https_steps = [
        "Load the TLS key log in Wireshark (see setup above)",
        f"Apply filter:  tcp.port == {HTTPS_PORT}",
        f"Open {HTTPS_URL}/auth/login  →  submit any credentials",
        "Switch filter to: http2",
        "Right-click the HEADERS or DATA frame → Follow → HTTP/2 Stream",
        "Read the decrypted POST body — credentials visible!",
        (
            "Key insight: HTTPS stops network attackers, "
            "not local key export"
        ),
    ]
    for i, s in enumerate(https_steps, 1):
        print(f"      {DIM(str(i) + '.')} {s}")

    print()
    print(BOLD("  🔑  Demo Credentials  (any will work)"))
    creds = [
        ("admin",   "password123"),
        ("alice",   "alice2024"),
        ("bob",     "letmein"),
        ("student", "demo1234"),
    ]
    for u, p in creds:
        print(f"      {CYAN(u):20s} → {YELLOW(p)}")

    print()
    print(line)
    print(YELLOW(
        "  ⚠  This demo runs on localhost only. "
        "Do not expose these ports externally."
    ))
    print(DIM(
        "  To reset between sessions: "
        "python scripts/reset_lab.py"
    ))
    print(line)
    print(DIM("  Press Ctrl+C to stop both servers."))
    print()


# ── Main ────────────────────────────────────────────────────────────────
def main() -> None:
    """Entry point — run the full setup and launch sequence.

    Returns:
        None
    """
    # Must happen before any multiprocessing.Process calls
    multiprocessing.freeze_support()

    check_python()
    setup_environment()
    ensure_certs()
    keylog = ensure_keylog()
    print_banner(keylog=keylog)

    http_proc, https_proc = start_servers()

    # Launch Chrome with SSL key logging in a background thread
    import threading
    chrome_thread = threading.Thread(
        target=launch_chrome_with_keylog,
        args=(keylog,),
        daemon=True,
    )
    chrome_thread.start()

    try:
        # Block until the user presses Ctrl+C
        while http_proc.is_alive() or https_proc.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(CYAN("\n\n  Shutting down demo servers …"))
    finally:
        http_proc.terminate()
        https_proc.terminate()
        http_proc.join(timeout=3)
        https_proc.join(timeout=3)
        print(GREEN("  ✓ Both servers stopped."))
        print(DIM(
            "  Run 'python scripts/reset_lab.py' to clear "
            "TLS keys before the next session.\n"
        ))


if __name__ == "__main__":
    main()
