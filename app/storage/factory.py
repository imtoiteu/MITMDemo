"""
Factory for StorageBackend instances.

High-level modules call get_storage() and receive the ABC type —
they never import a concrete class directly (Rule 4 / Rule 7).
"""

from app.storage.base import StorageBackend
from app.storage.memory_storage import MemoryStorage

# Module-level singleton shared across all requests in one process
_instance: StorageBackend | None = None


def get_storage() -> StorageBackend:
    """Return the application-wide storage singleton.

    Returns:
        A StorageBackend instance (MemoryStorage by default).
    """
    global _instance
    if _instance is None:
        _instance = MemoryStorage()
    return _instance
