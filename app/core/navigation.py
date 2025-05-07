"""
Navigation helper module.

This module provides functionality for generating navigation data
for the application templates using the centralized report registry.
"""

import logging
from app.core.report_registry import get_all_groups

# Configure logger
logger = logging.getLogger(__name__)


def get_navigation_data():
    """
    Generate navigation data for the application.

    This function returns structured data for the navbar
    containing groups and their associated reports.

    Returns:
        list: A list of dictionaries containing navigation data.
    """
    try:
        # Simply retrieve from the central registry
        nav_groups = get_all_groups()

        logger.info("Generated navigation data with %d groups", len(nav_groups))
        return nav_groups

    except Exception as e:
        logger.error("Error generating navigation data: %s", str(e))
        # Return empty list in case of error
        return []
