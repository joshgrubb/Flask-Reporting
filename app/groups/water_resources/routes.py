# app/groups/water_resources/routes.py
"""
Water Resources Module Routes.

This module defines routes for the main Water Resources dashboard.
"""

import logging
from flask import render_template

from app.groups.water_resources import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the Water Resources reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available reports
        reports = [
            {
                "id": "hydrant_history",
                "name": "Hydrant History",
                "description": "View hydrant inspection and work order history",
                "url": "/groups/water_resources/hydrant_history/",
                "icon": "fas fa-history",
            },
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Water Resources dashboard with %d reports", len(reports))

        return render_template(
            "groups/water_resources/dashboard.html",
            title="Water Resources Reports",
            reports=reports,
        )

    except Exception as e:
        logger.error("Error rendering Water Resources dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
