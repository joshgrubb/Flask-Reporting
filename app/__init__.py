"""
Application factory module.

This module contains the application factory function for creating Flask app instances.
"""

import os
import logging
from flask import Flask
from config import config

# Import database functions
from app.core.database import close_db_connections

# Import template helpers
from app.core.template_helpers import register_template_helpers


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name (str, optional): The configuration to use.
            Defaults to the APP_ENV environment variable or 'default'.

    Returns:
        Flask: The configured Flask application.
    """
    # Create Flask app
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Determine configuration to use
    if config_name is None:
        config_name = os.environ.get("APP_ENV", "default")

    # Load configuration
    app.config.from_object(config[config_name])

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"]),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Register database connection teardown
    app.teardown_appcontext(close_db_connections)

    # Register template helpers
    register_template_helpers(app)

    # Register blueprints
    from app.reports import bp as reports_bp

    app.register_blueprint(reports_bp)

    @app.route("/")
    def index():
        """Main application route redirects to reports dashboard."""
        from flask import redirect, url_for

        return redirect(url_for("reports.index"))

    return app
