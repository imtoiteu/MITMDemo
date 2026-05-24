"""
Home / landing page route.

Provides an overview of available demos and links to all pages.
"""

from flask import Blueprint, render_template

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index() -> str:
    """Render the landing page with demo navigation.

    Returns:
        Rendered HTML string.
    """
    return render_template("index.html")
