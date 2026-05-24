"""
conftest.py — Shared pytest fixtures.

All external I/O (filesystem, network) is mocked so tests
run completely offline with no real cert generation or servers.
"""

from collections.abc import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.app import create_app
from app.storage.factory import get_storage


@pytest.fixture()
def http_app() -> Flask:
    """Flask app configured in HTTP demo mode.

    Returns:
        Flask test application instance.
    """
    application = create_app(mode="http")
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    return application


@pytest.fixture()
def https_app() -> Flask:
    """Flask app configured in HTTPS demo mode.

    Returns:
        Flask test application instance.
    """
    application = create_app(mode="https")
    application.config["TESTING"] = True
    return application


@pytest.fixture()
def client(http_app: Flask) -> FlaskClient:
    """Test client for the HTTP-mode app.

    Args:
        http_app: The HTTP Flask app fixture.

    Returns:
        Flask test client.
    """
    return http_app.test_client()


@pytest.fixture(autouse=True)
def reset_storage() -> Generator[None, None, None]:
    """Reset in-memory storage before each test.

    Yields:
        None — setup/teardown fixture.
    """
    storage = get_storage()
    storage.clear_messages()
    yield
    storage.clear_messages()
