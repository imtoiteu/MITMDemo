"""
Unit tests for the home route.

Follows Red → Green → Refactor (Rule 5).
All external I/O is isolated via Flask test client.
"""

from flask.testing import FlaskClient


def test_index_get_returns_200(client: FlaskClient) -> None:
    """GET / should return HTTP 200.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_training_banner(client: FlaskClient) -> None:
    """Home page must render the training banner text.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"Security Awareness Training" in response.data


def test_index_contains_demo_scenarios(client: FlaskClient) -> None:
    """Home page must contain links to all four demo scenarios.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/")
    html = response.data
    assert b"Login Page" in html
    assert b"Chat" in html
    assert b"Bank Transfer" in html
    assert b"File Upload" in html


def test_index_http_mode_shows_warning(client: FlaskClient) -> None:
    """HTTP-mode app must show the unencrypted warning ribbon.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"UNENCRYPTED" in response.data


def test_index_https_mode_shows_secure(https_app: object) -> None:
    """HTTPS-mode app must show the TLS encrypted ribbon.

    Args:
        https_app: Flask HTTPS app fixture.
    """
    from flask import Flask
    app: Flask = https_app  # type: ignore[assignment]
    with app.test_client() as c:
        response = c.get("/")
        assert b"TLS ENCRYPTED" in response.data
