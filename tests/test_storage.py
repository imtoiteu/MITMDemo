"""
Unit tests for the in-memory storage backend.

Tests the concrete MemoryStorage class via the StorageBackend ABC
returned by the factory (Rule 4 / Rule 5).
"""

from datetime import datetime, timezone

import pytest

from app.schemas import ChatMessage
from app.storage.base import StorageBackend
from app.storage.factory import get_storage


@pytest.fixture()
def storage() -> StorageBackend:
    """Return a fresh storage instance for each test.

    Returns:
        StorageBackend instance with seeded messages cleared.
    """
    s = get_storage()
    s.clear_messages()
    return s


def test_storage_get_messages_returns_list(
    storage: StorageBackend,
) -> None:
    """get_messages() must return a list after clear.

    Args:
        storage: StorageBackend fixture.
    """
    # After clear, seed messages are restored
    msgs = storage.get_messages()
    assert isinstance(msgs, list)
    assert len(msgs) > 0  # seed messages restored


def test_storage_add_message_increases_count(
    storage: StorageBackend,
) -> None:
    """add_message() must increase the message count by one.

    Args:
        storage: StorageBackend fixture.
    """
    before = len(storage.get_messages())
    msg = ChatMessage(
        sender="Test",
        content="Hello storage",
        timestamp=datetime.now(timezone.utc),
    )
    storage.add_message(msg)
    after = len(storage.get_messages())
    assert after == before + 1


def test_storage_add_message_persists_content(
    storage: StorageBackend,
) -> None:
    """Stored message content must be retrievable unchanged.

    Args:
        storage: StorageBackend fixture.
    """
    msg = ChatMessage(
        sender="Alice",
        content="Super secret message",
        timestamp=datetime.now(timezone.utc),
    )
    storage.add_message(msg)
    messages = storage.get_messages()
    last = messages[-1]
    assert last.sender == "Alice"
    assert last.content == "Super secret message"


def test_storage_clear_restores_seed_messages(
    storage: StorageBackend,
) -> None:
    """clear_messages() must restore the Alice/Bob seed conversation.

    Args:
        storage: StorageBackend fixture.
    """
    storage.add_message(
        ChatMessage(
            sender="Extra",
            content="Extra message",
            timestamp=datetime.now(timezone.utc),
        )
    )
    storage.clear_messages()
    messages = storage.get_messages()
    senders = {m.sender for m in messages}
    assert "Alice" in senders
    assert "Bob" in senders
    assert "Extra" not in senders


def test_storage_get_messages_returns_copy(
    storage: StorageBackend,
) -> None:
    """get_messages() must return a copy so mutations don't affect storage.

    Args:
        storage: StorageBackend fixture.
    """
    messages = storage.get_messages()
    original_len = len(messages)
    messages.clear()  # Mutate the returned list
    assert len(storage.get_messages()) == original_len


def test_storage_session_set_and_get(
    storage: StorageBackend,
) -> None:
    """set_session_value / get_session_value must round-trip correctly.

    Args:
        storage: StorageBackend fixture.
    """
    storage.set_session_value("username", "alice")
    assert storage.get_session_value("username") == "alice"


def test_storage_session_missing_key_returns_none(
    storage: StorageBackend,
) -> None:
    """get_session_value for a missing key must return None.

    Args:
        storage: StorageBackend fixture.
    """
    result = storage.get_session_value("nonexistent_key")
    assert result is None


def test_factory_returns_storage_backend_abc(
    storage: StorageBackend,
) -> None:
    """The factory must return an instance of StorageBackend.

    Args:
        storage: StorageBackend fixture.
    """
    assert isinstance(storage, StorageBackend)


def test_factory_returns_singleton() -> None:
    """get_storage() must return the same instance on repeated calls.

    Returns:
        None
    """
    s1 = get_storage()
    s2 = get_storage()
    assert s1 is s2
