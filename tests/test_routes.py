"""
Unit tests for the chat, banking, and upload routes.

All external I/O is handled by the Flask test client.
No real network connections or disk writes occur.
"""

import io

from flask.testing import FlaskClient

# ── Chat tests ──────────────────────────────────────────────────────────

def test_chat_get_returns_200(client: FlaskClient) -> None:
    """GET /chat/ should return HTTP 200.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/chat/")
    assert response.status_code == 200


def test_chat_get_contains_seeded_messages(
    client: FlaskClient,
) -> None:
    """Chat page must render the pre-seeded Alice/Bob conversation.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/chat/")
    html = response.data
    assert b"Alice" in html
    assert b"Bob" in html


def test_chat_send_post_adds_message_and_redirects(
    client: FlaskClient,
) -> None:
    """POST /chat/send must store message and redirect (302).

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/chat/send",
        data={"sender": "Student", "content": "Hello from test!"},
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_chat_send_message_visible_after_redirect(
    client: FlaskClient,
) -> None:
    """Sent message content must appear on the chat page.

    Args:
        client: Flask test client fixture.
    """
    client.post(
        "/chat/send",
        data={"sender": "Eve", "content": "I am sniffing you!"},
    )
    response = client.get("/chat/")
    assert b"I am sniffing you!" in response.data


def test_chat_reset_clears_custom_messages(
    client: FlaskClient,
) -> None:
    """POST /chat/reset must remove user-added messages.

    Args:
        client: Flask test client fixture.
    """
    client.post(
        "/chat/send",
        data={"sender": "Student", "content": "Temporary message"},
    )
    client.post("/chat/reset")
    response = client.get("/chat/")
    assert b"Temporary message" not in response.data


def test_chat_send_empty_content_ignored(
    client: FlaskClient,
) -> None:
    """POST /chat/send with empty content must still redirect cleanly.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/chat/send",
        data={"sender": "Alice", "content": ""},
        follow_redirects=False,
    )
    assert response.status_code == 302


# ── Banking tests ───────────────────────────────────────────────────────

def test_banking_get_returns_200(client: FlaskClient) -> None:
    """GET /banking/ should return HTTP 200.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/banking/")
    assert response.status_code == 200


def test_banking_get_contains_form_fields(
    client: FlaskClient,
) -> None:
    """Banking page must contain all required form fields.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/banking/")
    html = response.data
    assert b'name="recipient"' in html
    assert b'name="amount"' in html
    assert b'name="note"' in html


def test_banking_post_valid_shows_confirmation(
    client: FlaskClient,
) -> None:
    """POST with valid data must show the transfer confirmation.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/banking/",
        data={
            "recipient": "John Smith",
            "account_number": "1234-5678",
            "amount": "500.00",
            "note": "Invoice 001",
        },
    )
    assert response.status_code == 200
    assert b"John Smith" in response.data
    assert b"500" in response.data


def test_banking_post_invalid_amount_shows_error(
    client: FlaskClient,
) -> None:
    """POST with a non-numeric amount must show an error.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/banking/",
        data={
            "recipient": "Jane",
            "account_number": "",
            "amount": "not-a-number",
            "note": "",
        },
    )
    assert response.status_code == 200
    assert (
        b"error" in response.data.lower()
        or b"required" in response.data.lower()
    )


def test_banking_post_exposes_capture_box_over_http(
    client: FlaskClient,
) -> None:
    """Confirmation page must show a capture box in HTTP mode.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/banking/",
        data={
            "recipient": "Eve Attacker",
            "account_number": "9999",
            "amount": "1000",
            "note": "stolen",
        },
    )
    assert b"POST body" in response.data or b"Wireshark" in response.data


# ── Upload tests ────────────────────────────────────────────────────────

def test_upload_get_returns_200(client: FlaskClient) -> None:
    """GET /upload/ should return HTTP 200.

    Args:
        client: Flask test client fixture.
    """
    response = client.get("/upload/")
    assert response.status_code == 200


def test_upload_post_no_file_shows_error(
    client: FlaskClient,
) -> None:
    """POST /upload/ with no file must return an error message.

    Args:
        client: Flask test client fixture.
    """
    response = client.post(
        "/upload/",
        data={},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"No file" in response.data


def test_upload_post_valid_file_shows_result(
    client: FlaskClient,
) -> None:
    """POST /upload/ with a valid file must return filename and size.

    The file content is held in memory only — never written to disk.

    Args:
        client: Flask test client fixture.
    """
    file_content = b"This is a demo secret file. Sniff me over HTTP!"
    response = client.post(
        "/upload/",
        data={"file": (io.BytesIO(file_content), "secret.txt")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"secret.txt" in response.data
    assert (
        b"not stored on disk" in response.data.lower()
        or b"discarded" in response.data.lower()
    )


def test_upload_post_reports_correct_size(
    client: FlaskClient,
) -> None:
    """Upload result must report the correct file size in bytes.

    Args:
        client: Flask test client fixture.
    """
    payload = b"A" * 1024  # exactly 1 KB
    response = client.post(
        "/upload/",
        data={"file": (io.BytesIO(payload), "test.bin")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    # 1024 bytes should appear in the response
    assert (
        b"1024" in response.data
        or b"1 KB" in response.data
        or b"1.0" in response.data
    )
