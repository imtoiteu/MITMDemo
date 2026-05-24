# MITMDemo - Windows Setup & Demo Guide

## 1. REQUIREMENTS

Install the following software first.

---

### 1. Python

Download:

https://www.python.org/downloads/windows/

> IMPORTANT:
>
> During installation, CHECK:
>
> - [x] Add Python to PATH

---

### 2. Git

Download:

https://git-scm.com/download/win

---

### 3. Wireshark

Download:

https://www.wireshark.org/download.html

> IMPORTANT:
>
> During installation, CHECK:
>
> - [x] Install Npcap
> - [x] Support loopback traffic ("Npcap Loopback Adapter")

---

### 4. Google Chrome

Download:

https://www.google.com/chrome/

---

# 2. CLONE REPOSITORY

Open CMD or PowerShell:

```powershell
git clone https://github.com/imtoiteu/MITMDemo.git
cd MITMDemo
```

---

# 3. START THE DEMO

Run:

```powershell
start-demo.bat
```

The script will automatically:

- Create Python virtual environment
- Install dependencies
- Generate TLS certificates
- Start HTTP server
- Start HTTPS server
- Launch Chrome with TLS session key logging
- Create:

```text
tlskeys\sslkeys.log
```

---

# 4. OPEN WIRESHARK

Open Wireshark.

Select interface:

- Npcap Loopback Adapter
- Adapter for loopback traffic capture

---

# 5. TEST CASE 1 — HTTP PLAINTEXT SNIFFING

## STEP 1 — Start Capture

Use filter:

```text
http
```

---

## STEP 2 — Open HTTP Website

```text
http://127.0.0.1:5000/auth/login
```

---

## STEP 3 — Login

Example credentials:

```text
username: alice
password: alice2024
```

---

## STEP 4 — Observe Wireshark

Apply filter:

```text
http.request.method == "POST"
```

You should see:

```text
POST /auth/login HTTP/1.1
```

Expand:

- Hypertext Transfer Protocol
- HTML Form URL Encoded

You will see plaintext credentials:

```text
username=alice
password=alice2024
```

---

### Result

HTTP traffic is **NOT encrypted**.

An attacker can sniff credentials directly.

---

# 6. TEST CASE 2 — HTTPS ENCRYPTED TRAFFIC

## STEP 1 — Clear Capture

Wireshark:

```text
Edit → Clear All
```

---

## STEP 2 — Start New Capture

Apply filter:

```text
tcp.port == 5443
```

---

## STEP 3 — Open HTTPS Website

```text
https://127.0.0.1:5443/auth/login
```

---

## STEP 4 — Login Again

---

## STEP 5 — Observe Wireshark

You should only see:

```text
TLSv1.3 Application Data
```

You CANNOT see:

- username
- password
- POST body

---

### Result

HTTPS encrypts the payload using TLS.

Attackers can still see:

- IP address
- port
- timing
- packet size

But cannot read the actual content.

---

# 7. TEST CASE 3 — HTTPS DECRYPTION USING TLS SESSION KEYS

## STEP 1 — Configure TLS Decryption

In Wireshark:

```text
Edit
→ Preferences
→ Protocols
→ TLS
```

Find:

```text
(Pre)-Master-Secret log filename
```

Select:

```text
tlskeys\sslkeys.log
```

---

## STEP 2 — Restart Capture

- Stop current capture
- Start capture again

---

## STEP 3 — Login HTTPS Again

```text
https://127.0.0.1:5443/auth/login
```

---

## STEP 4 — Apply Filter

Use:

```text
http2
```

OR:

```text
http.request.method == "POST"
```

---

## STEP 5 — Observe Decrypted HTTPS Traffic

You should now see:

```text
POST /auth/login
```

And plaintext credentials:

```text
username=alice
password=alice2024
```

---

### Result

Wireshark can decrypt HTTPS traffic
ONLY because the browser exported TLS session keys locally.

This demonstrates:

- HTTPS protects traffic in transit
- But compromised endpoints can still expose decrypted data

---

# 8. RESET LAB

To clean old TLS keys and reset the environment:

```powershell
python scripts/reset_lab.py
```

OR:

```powershell
reset-lab.bat
```

---

# 9. USEFUL WIRESHARK FILTERS

## All HTTP traffic

```text
http
```

---

## POST requests only

```text
http.request.method == "POST"
```

---

## All TLS traffic

```text
tls
```

---

## HTTPS demo traffic only

```text
tcp.port == 5443
```

---

## Decrypted HTTP/2 traffic

```text
http2
```

---

# 10. RECOMMENDED CLASSROOM FLOW

## Demo 1 — HTTP Credential Sniffing

→ Show plaintext credentials

---

## Demo 2 — HTTPS Encrypted Traffic

→ Show TLS Application Data only

---

## Demo 3 — HTTPS Decryption Using TLS Session Keys

→ Show decrypted HTTPS POST request

---

# Educational Purpose Only

This project is intended ONLY for:

- cybersecurity awareness
- HTTP vs HTTPS demonstrations
- TLS encryption education
- Wireshark learning labs

Use only in controlled local environments.
