"""
start_http.py — Start the demo server in HTTP mode (port 5000).

Usage:
    python scripts/start_http.py
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path when called directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.app import create_app
from app.config import settings


def main() -> None:
    """Start Flask in HTTP (plain) mode.

    Returns:
        None
    """
    app = create_app(mode="http")
    print(
        f"[http]  Starting HTTP server on "
        f"http://127.0.0.1:{settings.http_port}"
    )
    app.run(
        host="127.0.0.1",
        port=settings.http_port,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
