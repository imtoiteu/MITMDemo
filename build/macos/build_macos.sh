#!/usr/bin/env bash
# =============================================================
# build_macos.sh — Build AwarenessDemo.app with PyInstaller
#
# Prerequisites:
#   1. Python 3.10+  (brew install python)
#   2. uv installed  (brew install uv  OR  curl -LsSf https://astral.sh/uv/install.sh | sh)
#   3. Run from the project root:
#        chmod +x build/macos/build_macos.sh
#        ./build/macos/build_macos.sh
# =============================================================
set -euo pipefail

echo ""
echo "▶  [build] Installing PyInstaller …"
uv add --dev pyinstaller

echo ""
echo "▶  [build] Generating TLS certificate (if missing) …"
uv run python scripts/generate_cert.py

echo ""
echo "▶  [build] Running PyInstaller …"
uv run pyinstaller build/awareness_demo.spec \
    --distpath dist \
    --workpath build/work \
    --clean

echo ""
echo "✓  [build] Build complete!"
echo "   Output:  dist/AwarenessDemo.app"
echo ""
echo "   To run:  open dist/AwarenessDemo.app"
echo "   Or from terminal:  ./dist/AwarenessDemo/AwarenessDemo"
echo ""
