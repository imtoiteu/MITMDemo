#!/usr/bin/env bash
# reset-lab.sh — Reset the demo lab between sessions (macOS / Linux)
#
# Clears: TLS session keys, Chrome profile, any .pcapng captures
# Then recreates a fresh empty sslkeys.log ready for the next demo.
#
# Usage:
#   chmod +x reset-lab.sh
#   ./reset-lab.sh
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

PYTHON=".venv/bin/python"
if [ ! -f "$PYTHON" ]; then PYTHON="python3"; fi

"$PYTHON" scripts/reset_lab.py
