# 🛡️ Security Awareness Demo

> **Local lab environment — for educational use only.**
> Demonstrates the difference between HTTP and HTTPS traffic interception.
> No internet exposure. Localhost only.

---

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Quick Start (One Command)](#quick-start)
4. [Manual Setup](#manual-setup)
5. [Demo Scenarios](#demo-scenarios)
6. [Wireshark Guide](#wireshark-guide)
7. [HTTP vs HTTPS Demo Walkthrough](#http-vs-https-walkthrough)
8. [How HTTPS Decryption Works in the Demo](#https-decryption)
9. [Educational Concepts](#educational-concepts)
10. [Reset Lab](#reset-lab)
11. [Packaging (Windows & macOS)](#packaging)
12. [Running Tests](#running-tests)

---

## Overview

This project is a **classroom security awareness lab** built with Python and Flask.
It runs two identical web servers simultaneously:

| Mode  | URL                        | Traffic      |
|-------|----------------------------|--------------|
| HTTP  | http://127.0.0.1:5000      | **Plaintext** — visible in Wireshark |
| HTTPS | https://127.0.0.1:5443     | **Encrypted** — unreadable in Wireshark |

Students use Wireshark on the loopback interface to capture and compare traffic
between the two modes across four demo scenarios:

- 🔑 **Login** — credential exposure
- 💬 **Chat** — message interception
- 🏦 **Banking** — financial data leakage
- 📁 **File Upload** — file content interception

---

## Project Structure

```
DemoMITM/
├── app/
│   ├── __init__.py
│   ├── app.py              # Flask factory
│   ├── config.py           # Pydantic settings
│   ├── routes/
│   │   ├── auth.py         # /auth/login, /auth/logout
│   │   ├── banking.py      # /banking/
│   │   ├── chat.py         # /chat/
│   │   ├── home.py         # /
│   │   └── upload.py       # /upload/
│   ├── schemas/
│   │   └── models.py       # Pydantic data models
│   ├── storage/
│   │   ├── base.py         # StorageBackend ABC
│   │   ├── factory.py      # get_storage() factory
│   │   └── memory_storage.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── chat.html
│       ├── banking.html
│       └── upload.html
├── certs/                  # Auto-generated (git-ignored)
├── scripts/
│   ├── generate_cert.py    # Self-signed TLS cert generator
│   ├── start_http.py       # HTTP-only launcher
│   └── start_https.py      # HTTPS-only launcher
├── tests/                  # pytest test suite
├── build/
│   ├── awareness_demo.spec
│   ├── windows/build_windows.bat
│   └── macos/build_macos.sh
├── run.py                  # ← ONE-COMMAND LAUNCHER
├── pyproject.toml
├── requirements.txt
└── .env.example
```

---

## Quick Start

### Prerequisites

- **Python 3.10+** — [python.org](https://python.org)
- **uv** (recommended) — [astral.sh/uv](https://docs.astral.sh/uv/)

### macOS / Linux

```bash
git clone <repo-url> DemoMITM
cd DemoMITM
python run.py
```

### Windows

```bat
git clone <repo-url> DemoMITM
cd DemoMITM
python run.py
```

`run.py` automatically:

1. ✅ Checks Python version
2. ✅ Creates `.venv` and installs all dependencies via `uv sync`
3. ✅ Generates a self-signed TLS certificate in `certs/`
4. ✅ Creates `tlskeys/sslkeys.log` for Wireshark TLS decryption
5. ✅ Starts HTTP server on port **5000**
6. ✅ Starts HTTPS server on port **5443** (with session key logging)
7. ✅ Launches **Chrome** with `--ssl-key-log-file` automatically
8. ✅ Prints Wireshark filters, TLS decryption steps, and demo walkthrough

Press **Ctrl+C** to stop both servers.

### Alternative — classroom shell helper

```bash
# macOS / Linux
chmod +x start-demo.sh
./start-demo.sh

# Windows
start-demo.bat
```

---

## Manual Setup

If you prefer manual control:

```bash
# 1. Create virtual environment
uv venv

# 2. Install dependencies
uv sync

# 3. Generate TLS certificate
uv run python scripts/generate_cert.py

# 4a. Start HTTP server (terminal 1)
uv run python scripts/start_http.py

# 4b. Start HTTPS server (terminal 2)
uv run python scripts/start_https.py
```

### Environment variables

Copy `.env.example` to `.env` to customise ports or the secret key:

```bash
cp .env.example .env
```

| Variable            | Default                             | Description                   |
|---------------------|-------------------------------------|-------------------------------|
| `FLASK_SECRET_KEY`  | `demo-secret-key-change-...`        | Flask session signing key     |
| `HTTP_PORT`         | `5000`                              | HTTP server port              |
| `HTTPS_PORT`        | `5443`                              | HTTPS server port             |
| `AUTO_OPEN_BROWSER` | `true`                              | Open browser on startup       |

---

## Demo Scenarios

### 1. 🔑 Login Page (`/auth/login`)

Submit any of the demo credentials:

| Username  | Password    |
|-----------|-------------|
| `admin`   | `password123` |
| `alice`   | `alice2024`   |
| `bob`     | `letmein`     |
| `student` | `demo1234`    |

**Over HTTP:** The POST body `username=alice&password=alice2024` is fully
visible in Wireshark as plaintext.

**Over HTTPS:** The same POST is encrypted inside a TLS record.

---

### 2. 💬 Chat Page (`/chat/`)

Alice and Bob exchange pre-seeded messages demonstrating real-world risks.
You can add your own messages using any sender name.

**Over HTTP:** Every message, sender name, and session cookie is captured
in Wireshark by following the HTTP stream.

---

### 3. 🏦 Bank Transfer (`/banking/`)

Fill in a fake wire transfer: recipient, account number, amount, and note.

**Over HTTP:** All four fields appear in the POST body in plaintext —
a network attacker can read the exact transfer amount and recipient.

---

### 4. 📁 File Upload (`/upload/`)

Upload any file (max 16 MB). The file is read into memory and immediately
discarded — **never written to disk**.

**Over HTTP:** File content travels as `multipart/form-data` in plaintext.
Wireshark's *Export Objects → HTTP* can reconstruct the complete file
from the packet capture.

---

## Wireshark Guide

### Interface selection

| OS      | Loopback interface name          |
|---------|----------------------------------|
| macOS   | `lo0`                            |
| Linux   | `lo`                             |
| Windows | `Loopback Adapter` (requires Npcap) |

> **Windows users:** Install [Npcap](https://npcap.com/) to capture
> on the loopback adapter.

### Capture filters

Apply these in Wireshark's filter bar before starting a capture:

| Purpose                    | Filter                                              |
|----------------------------|-----------------------------------------------------|
| All HTTP traffic           | `tcp.port == 5000`                                  |
| POST requests only         | `tcp.port == 5000 && http.request.method == "POST"` |
| Session cookies            | `http.cookie`                                       |
| HTTPS traffic (encrypted)  | `tcp.port == 5443`                                  |

### How to read a POST body

1. Start Wireshark → select loopback → apply filter `tcp.port == 5000`
2. Submit the login form at `http://127.0.0.1:5000/auth/login`
3. In Wireshark, click the HTTP POST packet
4. Right-click → **Follow → HTTP Stream**
5. Scroll down to the request body — you will see:
   ```
   username=alice&password=alice2024
   ```

### Exporting an uploaded file

1. Capture on `tcp.port == 5000` while uploading a file
2. In Wireshark: **File → Export Objects → HTTP**
3. Find the multipart upload entry and click **Save**
4. The file is fully reconstructed from the packet capture

---

## HTTP vs HTTPS Walkthrough

This is the recommended classroom demonstration sequence:

```
Step 1  Open Wireshark → loopback interface → Start capture
Step 2  Apply filter:  tcp.port == 5000
Step 3  Open http://127.0.0.1:5000/auth/login
Step 4  Enter username: alice   password: alice2024   → Submit
Step 5  Wireshark → find POST packet → Follow → HTTP Stream
        ► You can read: username=alice&password=alice2024

Step 6  Change filter to:  tcp.port == 5443
Step 7  Open https://127.0.0.1:5443/auth/login
Step 8  Enter the same credentials → Submit
Step 9  Wireshark → find TLS packet → Inspect
        ► You can only read: "TLS Application Data" — no plaintext

Step 10 Repeat steps 1–9 for /chat/, /banking/, /upload/
```

---

## How HTTPS Decryption Works in the Demo

### Why Wireshark cannot normally decrypt HTTPS

When a browser connects to an HTTPS server, it negotiates a **TLS session key**
that is used to encrypt all traffic. This key is ephemeral — it is generated
fresh for each session and is never transmitted over the network.

Without the session key, Wireshark can only see:

```
TLS Application Data (encrypted):
  17 03 03 04 7f 3a c8 d1 9e f2 ... [opaque bytes]
```

Nothing inside the HTTPS request or response is readable.

### The SSLKEYLOGFILE mechanism

Modern browsers (Chrome, Firefox) support a standard called **NSS Key Log Format**.
When the environment variable `SSLKEYLOGFILE` is set — or Chrome is launched with
`--ssl-key-log-file` — the browser **writes the TLS session keys to a local file**
as each HTTPS connection is established.

This file looks like:

```
CLIENT_RANDOM a3f2c8d1... 9e4b7a2f...
CLIENT_RANDOM 7d9a1c3e... 4f8b2d6a...
```

Wireshark can read this file and use the session keys to **retroactively decrypt**
any captured HTTPS traffic that was encrypted with those keys.

### How the demo uses this

1. **Server-side** — `scripts/start_https.py` uses Python's `ssl.SSLContext.keylog_filename`
   (available since Python 3.8) to export server-side TLS keys.

2. **Browser-side** — `scripts/launch_browser.py` starts Chrome with:
   ```
   --ssl-key-log-file=./tlskeys/sslkeys.log
   --user-data-dir=./tlskeys/chrome_profile
   ```
   Both server and browser keys are written to the **same file**.

3. **Wireshark** — You point Wireshark at `tlskeys/sslkeys.log` once,
   and it automatically decrypts all matching TLS sessions in the capture.

### Why this only works in the local lab

- The keys are written to **your local disk** — an attacker on the network
  cannot access them.
- In a real-world attack, the attacker would need to compromise your machine
  to obtain the session keys.
- **This demonstrates an important principle:** HTTPS protects against
  *network-level eavesdropping*, not against local compromise.

### Step-by-step: Wireshark HTTPS decryption

```
Step 1  Start the demo:  python run.py
        ► Chrome opens automatically with SSL key logging enabled
        ► Keys accumulate in:  tlskeys/sslkeys.log

Step 2  Open Wireshark → select loopback interface (lo0 / Loopback)

Step 3  Configure TLS decryption:
        Edit → Preferences → Protocols → TLS
        (Pre)-Master-Secret log filename:
        → /path/to/DemoMITM/tlskeys/sslkeys.log
        Click OK

Step 4  Start capture — apply filter:  tcp.port == 5443

Step 5  In Chrome, go to:  https://127.0.0.1:5443/auth/login
        Submit credentials: alice / alice2024

Step 6  Switch Wireshark filter to:  http2
        ► HTTP/2 HEADERS and DATA frames are now visible!

Step 7  Right-click a DATA frame → Follow → HTTP/2 Stream
        ► You can read the decrypted POST body:
           :method = POST
           :path   = /auth/login
           username=alice&password=alice2024
```

### Display filters for HTTPS decryption

| Filter | What it shows |
|--------|---------------|
| `tls` | All TLS records (handshake + data) |
| `tcp.port == 5443` | All HTTPS traffic |
| `http2` | Decrypted HTTP/2 frames (requires key log) |
| `http2.headers` | HTTP/2 header frames (method, path, status) |
| `http.request.method == "POST"` | Decrypted POST requests |

### Important educational note

> This technique works **only** because we control the browser process on the
> local machine. A network attacker intercepting HTTPS traffic remotely
> **cannot** decrypt it — they do not have access to the local key log file.
> This is why HTTPS remains secure against network-level threats.

---

## Educational Concepts

### 🕵️ Packet Sniffing

Network sniffing is the act of capturing and analysing packets as they
travel across a network. Tools like Wireshark operate the network
interface in *promiscuous mode*, allowing it to capture all packets,
not just those addressed to the machine.

**Risk:** On unencrypted HTTP, an attacker on the same network (e.g., a
public WiFi hotspot) can read usernames, passwords, cookies, messages,
and file contents in real time.

**Mitigation:** Use HTTPS. The entire HTTP conversation is wrapped in
TLS — an attacker capturing packets sees only opaque ciphertext.

---

### 🧑‍💻 Man-in-the-Middle (MITM) Attack

A MITM attack occurs when an attacker secretly intercepts and relays
communications between two parties.

**Over HTTP:**
```
Alice ──► [ATTACKER reads & can modify] ──► Server
```
The attacker can read the plaintext AND alter the POST body
(e.g., change the bank transfer recipient) before forwarding it.

**Over HTTPS:**
```
Alice ──► [TLS record — attacker cannot read or modify] ──► Server
```
TLS provides both confidentiality (encryption) and integrity (MAC).
Any modification of the ciphertext causes the server to reject it.

---

### 🔓 Plaintext Credential Exposure

When a login form is submitted over HTTP, the browser sends:

```
POST /auth/login HTTP/1.1
Host: 127.0.0.1:5000
Content-Type: application/x-www-form-urlencoded

username=alice&password=alice2024
```

This is fully readable by any network observer. Even if the server
uses HTTPS elsewhere, a single HTTP login form exposes the password.

**Mitigation:**
- Always use HTTPS for every page, not just the login form.
- Use HSTS (HTTP Strict Transport Security) to prevent protocol downgrade.

---

### 🔒 TLS / HTTPS Protection

TLS (Transport Layer Security) protects HTTP traffic by:

1. **Authentication** — The server presents a certificate.
   The browser verifies it was signed by a trusted CA.
2. **Key Exchange** — Client and server negotiate a shared secret
   using asymmetric cryptography (e.g., ECDHE).
3. **Encryption** — All subsequent data is encrypted with a
   symmetric cipher (e.g., AES-256-GCM).
4. **Integrity** — A MAC (message authentication code) detects any
   tampering in transit.

The result: an attacker capturing HTTPS traffic sees only random-looking
bytes — the content, headers, and URL path are all hidden.

---

## Packaging

### Windows — Build `AwarenessDemo.exe`

```bat
# From the project root
build\windows\build_windows.bat
```

Output: `dist\AwarenessDemo.exe` — double-click to run.

### macOS — Build `AwarenessDemo.app`

```bash
chmod +x build/macos/build_macos.sh
./build/macos/build_macos.sh
```

Output: `dist/AwarenessDemo.app` — double-click or `open dist/AwarenessDemo.app`.

### Prerequisites for packaging

```bash
uv add --dev pyinstaller
```

---

## Reset Lab

Run between classroom sessions to start fresh:

```bash
# macOS / Linux
./reset-lab.sh

# Windows
reset-lab.bat

# Directly
python scripts/reset_lab.py
```

This will:

1. 🗑️  Remove `tlskeys/sslkeys.log` (old TLS session keys)
2. 🗑️  Remove `tlskeys/chrome_profile/` (old Chrome demo profile)
3. ✅  Recreate `tlskeys/` with a fresh empty `sslkeys.log`
4. 📋  Print next-step instructions

> **Between sessions:** always reset before a new group of students
> so they start with a clean capture and empty key log.

---

## Running Tests

```bash
# Install dev dependencies
uv sync

# Run full test suite
uv run pytest --tb=short

# Linting
uv run ruff check .

# Type checking
uv run mypy app/ tests/
```

All tests run offline — no real network connections or cert generation.

---

## Security Notice

> This project is designed **exclusively** for local educational use.
>
> - All servers bind to `127.0.0.1` only — no external network exposure.
> - No data is written to disk (uploads are held in memory only).
> - Session data is ephemeral — cleared when the server stops.
> - The self-signed certificate is for demo purposes only.
> - **Do not deploy this application to a public server.**

---

*Built for security awareness training. Not for production use.*
