"""
In-memory implementation of StorageBackend.

All data lives in Python lists/dicts and is lost when the process
exits — intentional for a demo that should leave no persistent traces.
"""

from datetime import datetime, timezone

from app.schemas import ChatMessage
from app.storage.base import StorageBackend

# Pre-seeded Alice/Bob conversation to illustrate HTTP sniffing
_SEED_MESSAGES: list[dict[str, str]] = [
    {
        "sender": "Alice",
        "content": "Hey Bob! Did you get the project files?",
    },
    {
        "sender": "Bob",
        "content": "Yes! My password is hunter2, keep it safe 😅",
    },
    {
        "sender": "Alice",
        "content": (
            "LOL please change that! Also, I'm logging in from "
            "the coffee shop WiFi right now..."
        ),
    },
    {
        "sender": "Bob",
        "content": (
            "Wait — are you on HTTP?! Anyone on the network "
            "can read this conversation!"
        ),
    },
]


class MemoryStorage(StorageBackend):
    """Thread-safe (GIL) in-memory storage for the demo."""

    def __init__(self) -> None:
        """Initialise with pre-seeded demo messages."""
        self._messages: list[ChatMessage] = [
            ChatMessage(
                sender=m["sender"],
                content=m["content"],
                timestamp=datetime.now(timezone.utc),
            )
            for m in _SEED_MESSAGES
        ]
        self._session: dict[str, str] = {}

    def add_message(self, message: ChatMessage) -> None:
        """Append a message to the in-memory list.

        Args:
            message: The ChatMessage to store.
        """
        self._messages.append(message)

    def get_messages(self) -> list[ChatMessage]:
        """Return a shallow copy of the message list.

        Returns:
            All stored ChatMessage objects.
        """
        return list(self._messages)

    def clear_messages(self) -> None:
        """Reset the message list to the seed conversation.

        Returns:
            None
        """
        self._messages = [
            ChatMessage(
                sender=m["sender"],
                content=m["content"],
                timestamp=datetime.now(timezone.utc),
            )
            for m in _SEED_MESSAGES
        ]

    def set_session_value(self, key: str, value: str) -> None:
        """Store a key/value pair.

        Args:
            key: Session key.
            value: Session value.
        """
        self._session[key] = value

    def get_session_value(self, key: str) -> str | None:
        """Retrieve a session value.

        Args:
            key: Session key.

        Returns:
            Value string or None.
        """
        return self._session.get(key)
