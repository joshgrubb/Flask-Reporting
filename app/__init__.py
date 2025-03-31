"""Flask application factory."""

import os
from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

# Initialize extensions
cache = Cache()


def create_app(config_name=None):
    """Create and configure the Flask application."""
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    from config import config

    config_name = config_name or os.environ.get("FLASK_ENV", "default")
    app.config.from_object(config[config_name])

    # Initialize extensions
    CORS(app)
    cache.init_app(app)

    # Register blueprints
    from app.core.routes import main

    app.register_blueprint(main)

    # Import and register report blueprints
    # This will be expanded as you add reports
    from app.reports.powerbi.routes import powerbi
    from app.reports.ssrs.routes import ssrs

    app.register_blueprint(powerbi)
    app.register_blueprint(ssrs)

    return app
