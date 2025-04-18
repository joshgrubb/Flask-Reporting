"""
Template Context Processors module.

This module defines context processors that make data available
to all templates in the application.
"""

import logging
from flask import Blueprint
from app.core.navigation import get_navigation_data

# Configure logger
logger = logging.getLogger(__name__)


def register_context_processors(app):
    """
    Register context processors with the Flask application.

    Args:
        app: The Flask application instance.
    """
    try:

        @app.context_processor
        def inject_navigation_data():
            """
            Make navigation data available to all templates.

            Returns:
                dict: Dictionary containing navigation data.
            """
            return {"nav_groups": get_navigation_data()}

        logger.info("Registered template context processors")

    except Exception as e:
        logger.error("Error registering context processors: %s", str(e))
