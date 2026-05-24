"""
Typed application settings loaded from environment variables.

All runtime configuration lives here; no raw os.environ access
is allowed in business logic (Rule 3 / Rule 7).
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration resolved from .env or environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Flask session signing key — change for any non-demo deployment
    flask_secret_key: str = Field(
        default="demo-secret-key-change-in-production",
        alias="FLASK_SECRET_KEY",
    )

    # Label shown in the UI banner
    demo_mode_label: str = Field(
        default="Security Awareness Training",
        alias="DEMO_MODE_LABEL",
    )

    # Server ports
    http_port: int = Field(default=5000, alias="HTTP_PORT")
    https_port: int = Field(default=5443, alias="HTTPS_PORT")

    # Whether to auto-open the browser on startup
    auto_open_browser: bool = Field(
        default=True,
        alias="AUTO_OPEN_BROWSER",
    )

    # Paths (relative to project root)
    cert_file: str = "certs/cert.pem"
    key_file: str = "certs/key.pem"

    # TLS session key log — used for Wireshark HTTPS decryption demo.
    # The directory and file are created automatically at startup.
    # EDUCATIONAL USE ONLY: keys are written locally to this machine.
    tlskeys_dir: str = "tlskeys"
    keylog_file: str = "tlskeys/sslkeys.log"


# Module-level singleton — import this everywhere
settings = Settings()
