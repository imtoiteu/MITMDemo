"""Pydantic schemas for all demo data models."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class LoginForm(BaseModel):
    """Credentials submitted via the login form."""

    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class ChatMessage(BaseModel):
    """A single chat message between demo participants."""

    sender: str = Field(..., min_length=1, max_length=32)
    content: str = Field(..., min_length=1, max_length=512)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class BankTransfer(BaseModel):
    """A fake banking transfer request for demonstration."""

    recipient: str = Field(..., min_length=1, max_length=64)
    amount: float = Field(..., gt=0)
    note: str = Field(default="", max_length=256)
    account_number: str = Field(default="", max_length=32)


class UploadResult(BaseModel):
    """Result returned after a demo file upload."""

    filename: str
    size_bytes: int
    mime_type: str
    safe: bool = True
    message: str = "File received (demo only — not stored on disk)"
