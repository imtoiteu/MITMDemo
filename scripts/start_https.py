"""
start_https.py — Start the demo server in HTTPS mode (port 5443).

EDUCATIONAL TLS KEY LOGGING:
  Python 3.8+ ssl.SSLContext supports keylog_filename.  When set, the
  TLS pre-master secrets for every handshake are appended to the file
  specified by settings.keylog_file (tlskeys/sslkeys.log by default).

  Wireshark can load that file via:
    Preferences → Protocols → TLS
    → (Pre)-Master-Secret log filename → sslkeys.log

  This allows decryption of HTTPS traffic that was otherwise opaque.
  This is ONLY possible because we control the local server process.
  In production you would NEVER export session keys.

Requirements:
  certs/cert.pem and certs/key.pem must exist.
  Run scripts/generate_cert.py first, or use run.py which does both.

Usage:
    python scripts/start_https.py
"""

import ssl
import sys
from pathlib import Path

# Ensure project root is on sys.path when called directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.app import create_app
from app.config import settings


def _ensure_keylog_dir() -> Path:
    """Create the tlskeys directory and empty log file if missing.

    Returns:
        Absolute path to the sslkeys.log file.
    """
    keylog = Path(settings.keylog_file).resolve()
    keylog.parent.mkdir(parents=True, exist_ok=True)
    # Touch the file so Wireshark can be pointed at it before capture
    if not keylog.exists():
        keylog.touch()
    return keylog


def _build_ssl_context(cert: Path, key: Path, keylog: Path) -> ssl.SSLContext:
    """Build a TLS server context with session-key logging enabled.

    The keylog_filename attribute (Python >= 3.8) causes the ssl
    module to write NSS key log entries for every TLS handshake.
    Wireshark and other tools can parse this format to decrypt captures.

    Args:
        cert:   Path to the PEM certificate file.
        key:    Path to the PEM private key file.
        keylog: Path to the SSLKEYLOGFILE output.

    Returns:
        Configured ssl.SSLContext ready for use with Flask/Werkzeug.
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(certfile=str(cert), keyfile=str(key))

    # Enable TLS session key export (Python 3.8+)
    # This writes NSS Key Log entries so Wireshark can decrypt the traffic.
    ctx.keylog_filename = str(keylog)

    return ctx


def main() -> None:
    """Start Flask in HTTPS (TLS) mode with session key logging.

    Returns:
        None
    """
    cert = Path(settings.cert_file)
    key = Path(settings.key_file)

    if not cert.exists() or not key.exists():
        print(
            "[https] ERROR: Certificate files not found. "
            "Run 'python scripts/generate_cert.py' first."
        )
        sys.exit(1)

    keylog = _ensure_keylog_dir()

    print(
        f"[https] Starting HTTPS server on "
        f"https://127.0.0.1:{settings.https_port}"
    )
    print(f"[https] TLS session keys → {keylog}")
    print(
        "[https] Load in Wireshark: "
        "Preferences → Protocols → TLS → (Pre)-Master-Secret log filename"
    )

    ssl_ctx = _build_ssl_context(cert, key, keylog)

    app = create_app(mode="https")
    app.run(
        host="127.0.0.1",
        port=settings.https_port,
        debug=False,
        use_reloader=False,
        ssl_context=ssl_ctx,
    )


if __name__ == "__main__":
    main()
