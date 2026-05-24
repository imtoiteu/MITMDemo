"""
Unit tests for the authentication routes.

Covers:
  - GET /auth/login renders the login page
  - POST with valid credentials redirects to home
  - POST with invalid credentials shows error
  - POST body contains submitted values (educational capture box)
  - Logout clears session
"""

from flask.testing import FlaskClient


def test_login_get_returns_200(client: FlaskClient) -> None:
    """GET /auth/login should return HTTP 200.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/auth/login")
    assert response.status_code == 200


def test_login_get_contains_form(client: FlaskClient) -> None:
    """Login page must contain username and password fields.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/auth/login")
    html = response.data
    assert b'name="username"' in html
    assert b'name="password"' in html


def test_login_post_valid_credentials_redirects(
    client: FlaskClient,
) -> None:
    """POST with valid credentials must redirect (302) to home.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/" in response.headers["Location"]


def test_login_post_invalid_credentials_shows_error(
    client: FlaskClient,
) -> None:
    """POST with wrong password must return 200 with an error message.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrongpassword"},
    )
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_login_post_unknown_user_shows_error(
    client: FlaskClient,
) -> None:
    """POST with an unknown username must show error message.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "anything"},
    )
    assert response.status_code == 200
    assert b"Invalid" in response.data


def test_login_post_shows_submitted_values_in_capture_box(
    client: FlaskClient,
) -> None:
    """After a failed login, submitted values appear in the capture box.

    This is the educational feature that shows students exactly what
    would be visible in a Wireshark packet capture over HTTP.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/auth/login",
        data={"username": "alice", "password": "wrongpw"},
    )
    html = response.data
    assert b"alice" in html
    assert b"wrongpw" in html


def test_login_post_empty_fields_shows_error(
    client: FlaskClient,
) -> None:
    """POST with empty fields must show a validation error.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/auth/login",
        data={"username": "", "password": ""},
    )
    assert response.status_code == 200
    assert b"fill in" in response.data.lower() or b"Invalid" in response.data


def test_logout_clears_session_and_redirects(
    client: FlaskClient,
) -> None:
    """GET /auth/logout must clear session and redirect to home.

    Args:
        client: Flask test client fixture.
    """
    # First log in
    client.post(
        "/auth/login",
        data={"username": "alice", "password": "alice2024"},
        follow_redirects=True,
    )
    # Then log out
    response = client.get(
        "/auth/logout", follow_redirects=False
    )
    assert response.status_code == 302

    # Session should be cleared — next request should not carry username
    response2 = client.get("/")
    assert b"alice" not in response2.data or b"Logout" not in response2.data
