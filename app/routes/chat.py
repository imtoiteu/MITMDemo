"""
Chat routes — Alice/Bob demo messaging.

EDUCATIONAL NOTE:
  Each POST to /chat/send transmits the message body in plaintext
  over HTTP. A Wireshark capture on tcp.port == 5000 will show the
  full message content, sender name, and session cookie.

  Over HTTPS (port 5443) all of this is encrypted inside TLS records.
"""

from datetime import datetime, timezone

from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.wrappers import Response

from app.schemas import ChatMessage
from app.storage.factory import get_storage

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


@chat_bp.route("/")
def chat_home() -> str:
    """Render the chat page with all current messages.

    Returns:
        Rendered HTML string.
    """
    storage = get_storage()
    messages = storage.get_messages()
    return render_template("chat.html", messages=messages)


@chat_bp.route("/send", methods=["POST"])
def send_message() -> Response:
    """Accept a new chat message and redirect back to chat.

    The POST body (sender + content) is intentionally transmitted
    as plaintext over HTTP for demonstration purposes.

    Returns:
        Redirect response to the chat page.
    """
    sender = request.form.get("sender", "Anonymous").strip()
    content = request.form.get("content", "").strip()

    if sender and content:
        try:
            msg = ChatMessage(
                sender=sender[:32],
                content=content[:512],
                timestamp=datetime.now(timezone.utc),
            )
            get_storage().add_message(msg)
        except Exception:
            pass  # Silently drop malformed messages in demo

    return redirect(url_for("chat.chat_home"))


@chat_bp.route("/reset", methods=["POST"])
def reset_chat() -> Response:
    """Reset the chat to the seeded Alice/Bob conversation.

    Returns:
        Redirect response to the chat page.
    """
    get_storage().clear_messages()
    return redirect(url_for("chat.chat_home"))
