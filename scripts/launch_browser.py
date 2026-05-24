"""
launch_browser.py — Launch Chrome/Chromium with SSL key logging enabled.

EDUCATIONAL PURPOSE:
  This script starts Chrome with two special flags:
    --ssl-key-log-file=<path>   — Chrome writes TLS session keys to this file
    --user-data-dir=<temp>      — Isolated throwaway profile for the demo

  The combination lets Wireshark decrypt HTTPS traffic captured during
  the demo session.  The keys only cover this browser process — no
  system-wide key logging occurs.

SAFETY:
  - Keys are written to a local file under the project directory only.
  - The Chrome profile is a temporary directory deleted on reset.
  - Nothing is sent outside localhost.

Usage:
    python scripts/launch_browser.py [URL]

    URL defaults to https://127.0.0.1:5443/
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Ensure project root is on sys.path when called directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings

# ── URL to open ─────────────────────────────────────────────────────────
DEFAULT_URL = f"https://127.0.0.1:{settings.https_port}/"

# ── Temporary Chrome profile directory ──────────────────────────────────
# Stored inside the project so reset_lab.py can wipe it easily.
CHROME_PROFILE_DIR = (
    Path(__file__).parent.parent / "tlskeys" / "chrome_profile"
)


def _find_chrome() -> str | None:
    """Search for Chrome or Chromium executable on the current platform.

    Returns:
        Absolute path to the Chrome executable, or None if not found.
    """
    system = platform.system()

    if system == "Darwin":
        candidates = [
            Path(
                "/Applications/Google Chrome.app"
                "/Contents/MacOS/Google Chrome"
            ),
            Path(
                "/Applications/Chromium.app"
                "/Contents/MacOS/Chromium"
            ),
            Path(
                "/Applications/Google Chrome Canary.app"
                "/Contents/MacOS/Google Chrome Canary"
            ),
        ]
        for path in candidates:
            if path.exists():
                return str(path)

    elif system == "Windows":
        import os

        win_candidates = [
            Path(
                os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                r"Google\Chrome\Application\chrome.exe",
            ),
            Path(
                os.environ.get(
                    "PROGRAMFILES(X86)", r"C:\Program Files (x86)"
                ),
                r"Google\Chrome\Application\chrome.exe",
            ),
            Path(
                os.environ.get("LOCALAPPDATA", ""),
                r"Google\Chrome\Application\chrome.exe",
            ),
            Path(
                os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                r"Chromium\Application\chrome.exe",
            ),
        ]
        for path in win_candidates:
            if path.exists():
                return str(path)

    else:
        # Linux / other Unix
        for name in [
            "google-chrome",
            "google-chrome-stable",
            "chromium-browser",
            "chromium",
        ]:
            found = shutil.which(name)
            if found:
                return found

    return None


def launch_chrome(url: str = DEFAULT_URL) -> subprocess.Popen:  # type: ignore[type-arg]
    """Launch Chrome with SSL key logging and an isolated profile.

    Args:
        url: The URL to open on launch.

    Returns:
        The subprocess.Popen handle for the Chrome process.

    Raises:
        RuntimeError: If Chrome/Chromium cannot be found.
    """
    chrome = _find_chrome()
    if chrome is None:
        raise RuntimeError(
            "Chrome or Chromium not found. "
            "Please install Google Chrome and try again.\n"
            "Download: https://www.google.com/chrome/"
        )

    # Prepare the TLS key log path
    keylog = Path(settings.keylog_file).resolve()
    keylog.parent.mkdir(parents=True, exist_ok=True)
    if not keylog.exists():
        keylog.touch()

    # Prepare the isolated Chrome profile directory
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    args = [
        chrome,
        # ── Key logging ──────────────────────────────────────────────
        f"--ssl-key-log-file={keylog}",
        # ── Isolated throwaway profile ───────────────────────────────
        f"--user-data-dir={CHROME_PROFILE_DIR}",
        # ── Self-signed cert — accept without user prompt ────────────
        "--ignore-certificate-errors",
        "--ignore-ssl-errors",
        # ── Misc demo flags ──────────────────────────────────────────
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-extensions",
        "--disable-sync",
        "--disable-background-networking",
        # ── Open the demo URL ─────────────────────────────────────────
        url,
    ]

    print(f"[browser] Launching Chrome: {chrome}")
    print(f"[browser] SSL key log    → {keylog}")
    print(f"[browser] Chrome profile → {CHROME_PROFILE_DIR}")
    print(f"[browser] Opening URL    → {url}")

    return subprocess.Popen(args)


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    try:
        proc = launch_chrome(url)
        print(
            f"[browser] Chrome started (PID {proc.pid}). "
            "Close the window when done."
        )
    except RuntimeError as e:
        print(f"[browser] ERROR: {e}")
        sys.exit(1)
