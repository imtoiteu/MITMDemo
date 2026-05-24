"""
Abstract base class for the demo message/session storage backend.

Follows Rule 4: all contracts live in base.py; no business logic here.
"""

from abc import ABC, abstractmethod

from app.schemas import ChatMessage


class StorageBackend(ABC):
    """Contract for storing and retrieving chat messages and sessions."""

    @abstractmethod
    def add_message(self, message: ChatMessage) -> None:
        """Persist a chat message.

        Args:
            message: The ChatMessage to store.
        """
        ...

    @abstractmethod
    def get_messages(self) -> list[ChatMessage]:
        """Return all stored chat messages in insertion order.

        Returns:
            List of ChatMessage objects.
        """
        ...

    @abstractmethod
    def clear_messages(self) -> None:
        """Remove all stored messages (reset for new demo session).

        Returns:
            None
        """
        ...

    @abstractmethod
    def set_session_value(self, key: str, value: str) -> None:
        """Store an arbitrary key/value pair for the current session.

        Args:
            key: Session key.
            value: Session value.
        """
        ...

    @abstractmethod
    def get_session_value(self, key: str) -> str | None:
        """Retrieve a session value by key.

        Args:
            key: Session key to look up.

        Returns:
            The stored value, or None if not present.
        """
        ...
