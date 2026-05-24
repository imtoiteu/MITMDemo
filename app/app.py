"""
Flask application factory.

Usage:
    from app.app import create_app
    app = create_app()
"""

from flask import Flask

from app.config import settings
from app.routes.auth import auth_bp
from app.routes.banking import banking_bp
from app.routes.chat import chat_bp
from app.routes.home import home_bp
from app.routes.upload import upload_bp


def create_app(mode: str = "http") -> Flask:
    """Construct and configure the Flask application.

    Args:
        mode: Either ``"http"`` or ``"https"``.
              Stored in app.config so templates can display a banner.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Session signing key from settings (never raw os.environ)
    app.config["SECRET_KEY"] = settings.flask_secret_key

    # Expose the mode and label to every template via context_processor
    app.config["DEMO_MODE"] = mode.upper()
    app.config["DEMO_LABEL"] = settings.demo_mode_label

    @app.context_processor
    def inject_demo_globals() -> dict:  # type: ignore[type-arg]
        """Inject demo metadata into every template context.

        Returns:
            Dictionary of template variables.
        """
        return {
            "demo_mode": app.config["DEMO_MODE"],
            "demo_label": app.config["DEMO_LABEL"],
            "http_port": settings.http_port,
            "https_port": settings.https_port,
        }

    # Register all blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(banking_bp)
    app.register_blueprint(upload_bp)

    return app
