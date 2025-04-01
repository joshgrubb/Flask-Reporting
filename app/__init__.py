"""
Application factory module.

This module contains the application factory function for creating Flask app instances.
"""

import os
import logging
from flask import Flask
from config import config

# Import database functions
from app.core.database import close_db_connection


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
    app = Flask(__name__)

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
    app.teardown_appcontext(close_db_connection)

    # Register blueprints here (will be added later)
    # from app.reports.powerbi import bp as powerbi_bp
    # app.register_blueprint(powerbi_bp)

    @app.route("/")
    def index():
        """Basic route for testing."""
        return "Flask Reporting Application"

    return app
