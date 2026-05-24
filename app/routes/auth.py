"""
Authentication routes — login and logout.

EDUCATIONAL NOTE:
  Over HTTP, the POST body containing username and password travels
  as plaintext. Students can capture this in Wireshark with the
  filter: tcp.port == 5000 && http.request.method == "POST"

  Over HTTPS (port 5443) the same POST is TLS-encrypted and only
  the encrypted bytes are visible — demonstrating why HTTPS matters.
"""

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.wrappers import Response

from app.schemas import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Demo-only credential store (plaintext intentional for demonstration)
# In a real application NEVER store passwords in plaintext.
_DEMO_USERS: dict[str, str] = {
    "admin": "password123",
    "alice": "alice2024",
    "bob": "letmein",
    "student": "demo1234",
}


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    """Handle the login form.

    GET  — Render the login page.
    POST — Validate credentials and redirect, or show error.
           The POST body (username + password) is INTENTIONALLY
           transmitted as plaintext over HTTP for demonstration.

    Returns:
        Rendered template or redirect response.
    """
    error: str | None = None
    submitted: dict[str, str] = {}

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Capture submitted values so the template can show them
        # (educational: students see exactly what was sent)
        submitted = {"username": username, "password": password}

        try:
            # Validate structure with pydantic
            form = LoginForm(username=username, password=password)

            # Check against demo credential store
            stored_pw = _DEMO_USERS.get(form.username)
            if stored_pw and stored_pw == form.password:
                session["logged_in"] = True
                session["username"] = form.username
                return redirect(url_for("home.index"))
            else:
                error = "Invalid username or password."

        except Exception:
            error = "Please fill in both fields."

    return render_template(
        "login.html",
        error=error,
        submitted=submitted,
        demo_users=_DEMO_USERS,
    )


@auth_bp.route("/logout")
def logout() -> Response:
    """Clear the session and redirect to home.

    Returns:
        Redirect response to the index page.
    """
    session.clear()
    return redirect(url_for("home.index"))
