"""
generate_cert.py — Self-signed TLS certificate generator.

Generates a 2048-bit RSA certificate valid for 365 days and writes:
  certs/cert.pem
  certs/key.pem

Usage:
    python scripts/generate_cert.py

Requires: cryptography (installed via uv sync)
"""

import datetime
import ipaddress
import os
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# Output paths (relative to project root)
CERT_DIR = Path(__file__).parent.parent / "certs"
CERT_FILE = CERT_DIR / "cert.pem"
KEY_FILE = CERT_DIR / "key.pem"


def generate_self_signed_cert() -> None:
    """Generate a self-signed RSA certificate and private key.

    Writes cert.pem and key.pem to the certs/ directory.
    Skips generation if both files already exist.

    Returns:
        None
    """
    CERT_DIR.mkdir(exist_ok=True)

    if CERT_FILE.exists() and KEY_FILE.exists():
        print(
            "[cert] Certificates already exist — "
            "skipping generation."
        )
        return

    print("[cert] Generating self-signed certificate …")

    # 1. Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 2. Build the certificate subject / issuer
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(
                NameOID.COUNTRY_NAME, "US"
            ),
            x509.NameAttribute(
                NameOID.STATE_OR_PROVINCE_NAME, "Demo State"
            ),
            x509.NameAttribute(
                NameOID.LOCALITY_NAME, "Demo City"
            ),
            x509.NameAttribute(
                NameOID.ORGANIZATION_NAME,
                "Security Awareness Demo",
            ),
            x509.NameAttribute(
                NameOID.COMMON_NAME, "127.0.0.1"
            ),
        ]
    )

    # 3. Validity window: now → +365 days
    now = datetime.datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=365))
        # Subject Alternative Names so browsers accept it for localhost
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName("localhost"),
                    x509.IPAddress(
                        ipaddress.IPv4Address("127.0.0.1")
                    ),
                ]
            ),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    # 4. Write private key (PEM, unencrypted for demo convenience)
    KEY_FILE.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    # 5. Write certificate
    CERT_FILE.write_bytes(
        cert.public_bytes(serialization.Encoding.PEM)
    )

    # Lock down permissions on Unix-like systems
    if os.name != "nt":
        KEY_FILE.chmod(0o600)
        CERT_FILE.chmod(0o644)

    print(f"[cert] ✓ Certificate written to {CERT_FILE}")
    print(f"[cert] ✓ Private key  written to {KEY_FILE}")
    print(
        "[cert] NOTE: This is a self-signed cert for "
        "local demo use only. Browsers will show a warning — "
        "click 'Advanced → Proceed' to continue."
    )


if __name__ == "__main__":
    generate_self_signed_cert()
