#!/usr/bin/env bash
# =============================================================
# start-demo.sh — One-command classroom launcher (macOS / Linux)
#
# What this does:
#   1. Activates the Python virtual environment
#   2. Generates TLS certificate if missing
#   3. Starts the HTTPS demo server (port 5443) with TLS key logging
#   4. Starts the HTTP demo server  (port 5000)
#   5. Launches Chrome with --ssl-key-log-file for HTTPS decryption
#   6. Prints exact Wireshark configuration steps
#
# Usage:
#   chmod +x start-demo.sh
#   ./start-demo.sh
# =============================================================
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

KEYLOG_FILE="$PROJECT_ROOT/tlskeys/sslkeys.log"
HTTPS_PORT=5443
HTTP_PORT=5000

# ── Colours ───────────────────────────────────────────────────────────
RED='\033[0;91m'; GREEN='\033[0;92m'; YELLOW='\033[0;93m'
CYAN='\033[0;96m'; BOLD='\033[1m'; RESET='\033[0m'

info()  { echo -e "${CYAN}▶  $*${RESET}"; }
ok()    { echo -e "${GREEN}   ✓  $*${RESET}"; }
warn()  { echo -e "${YELLOW}   ⚠  $*${RESET}"; }
fatal() { echo -e "${RED}   ✗  $*${RESET}"; exit 1; }

# ── 0. Print header ───────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║      🛡️  Security Awareness Demo — HTTPS Decryption Lab      ║${RESET}"
echo -e "${BOLD}${CYAN}║                  Local lab — educational use only            ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

# ── 1. Ensure venv exists ─────────────────────────────────────────────
info "Checking virtual environment …"
if command -v uv &>/dev/null; then
    uv sync --no-dev -q
    PYTHON=".venv/bin/python"
    ok "uv venv ready"
elif [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
    ok "Existing venv found"
else
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt -q
    PYTHON=".venv/bin/python"
    ok "venv created with pip"
fi

# ── 2. Generate TLS cert if missing ───────────────────────────────────
info "Checking TLS certificate …"
if [ ! -f "certs/cert.pem" ] || [ ! -f "certs/key.pem" ]; then
    $PYTHON scripts/generate_cert.py
    ok "Self-signed certificate generated"
else
    ok "Certificate already present"
fi

# ── 3. Ensure TLS key log file exists ─────────────────────────────────
info "Setting up TLS session key log …"
mkdir -p tlskeys
touch "$KEYLOG_FILE"
ok "Key log ready: $KEYLOG_FILE"

# ── 4. Start HTTPS server in background ───────────────────────────────
info "Starting HTTPS server (port $HTTPS_PORT) …"
$PYTHON scripts/start_https.py &
HTTPS_PID=$!
ok "HTTPS server PID: $HTTPS_PID"

# ── 5. Start HTTP server in background ────────────────────────────────
info "Starting HTTP server (port $HTTP_PORT) …"
$PYTHON scripts/start_http.py &
HTTP_PID=$!
ok "HTTP server PID: $HTTP_PID"

# ── 6. Wait for servers to bind ───────────────────────────────────────
sleep 1.5

# ── 7. Launch Chrome with SSL key logging ─────────────────────────────
info "Launching Chrome with SSL key logging …"
$PYTHON scripts/launch_browser.py "https://127.0.0.1:$HTTPS_PORT/" &
BROWSER_PID=$!
ok "Chrome started"

# ── 8. Print Wireshark configuration ──────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  🦈  WIRESHARK SETUP — Step by Step${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${BOLD}Step 1${RESET}  Open Wireshark"
echo -e "          Select interface: ${CYAN}lo0${RESET} (macOS loopback)"
echo ""
echo -e "  ${BOLD}Step 2${RESET}  Configure TLS decryption:"
echo -e "          ${YELLOW}Wireshark → Preferences → Protocols → TLS${RESET}"
echo -e "          (Pre)-Master-Secret log filename:"
echo -e "          ${CYAN}$KEYLOG_FILE${RESET}"
echo ""
echo -e "  ${BOLD}Step 3${RESET}  Start capture — apply display filter:"
echo -e "          ${CYAN}tcp.port == $HTTPS_PORT${RESET}"
echo ""
echo -e "  ${BOLD}Step 4${RESET}  In Chrome, go to:"
echo -e "          ${CYAN}https://127.0.0.1:$HTTPS_PORT/auth/login${RESET}"
echo -e "          Submit any demo credentials"
echo ""
echo -e "  ${BOLD}Step 5${RESET}  In Wireshark, switch filter to:"
echo -e "          ${CYAN}http2${RESET}   or   ${CYAN}http.request.method == \"POST\"${RESET}"
echo -e "          You will see the DECRYPTED HTTP/2 POST with credentials!"
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${BOLD}🔑  TLS key log file:${RESET}  ${CYAN}$KEYLOG_FILE${RESET}"
echo ""
echo -e "  ${BOLD}📋  Display filters:${RESET}"
echo -e "      ${CYAN}tls${RESET}                              — all TLS records"
echo -e "      ${CYAN}http2${RESET}                            — decrypted HTTP/2 frames"
echo -e "      ${CYAN}tcp.port == $HTTPS_PORT${RESET}                 — HTTPS traffic"
echo -e "      ${CYAN}http.request.method == \"POST\"${RESET}    — login/form submissions"
echo ""
echo -e "  ${YELLOW}⚠  Press Ctrl+C to stop all servers and exit${RESET}"
echo ""

# ── 9. Wait and cleanup ───────────────────────────────────────────────
cleanup() {
    echo -e "\n${CYAN}  Shutting down …${RESET}"
    kill "$HTTPS_PID" "$HTTP_PID" 2>/dev/null || true
    wait "$HTTPS_PID" "$HTTP_PID" 2>/dev/null || true
    echo -e "${GREEN}  ✓  Servers stopped.${RESET}"
    echo -e "${CYAN}  Tip: Run './reset-lab.sh' to clear TLS keys before next session.${RESET}\n"
}
trap cleanup EXIT INT TERM

wait "$HTTPS_PID"
