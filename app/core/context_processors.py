"""
Template Context Processors module.

This module defines context processors that make data available
to all templates in the application.
"""

import logging
from flask import Blueprint
from app.core.report_registry import get_all_groups, get_all_reports

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
        def inject_reports_data():
            """Inject reports data into all templates."""
            return {"nav_groups": get_all_groups(), "all_reports": get_all_reports()}

        logger.info("Registered template context processors")

    except Exception as e:
        logger.error("Error registering context processors: %s", str(e))
