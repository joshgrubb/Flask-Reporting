"""
Community Development Module Routes.

This module defines routes for the main Community Development dashboard.
"""

import logging
from flask import render_template

from app.groups.community_development import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the Community Development reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available reports
        reports = [
            {
                "id": "bluebeam",
                "name": "Bluebeam Development Projects",
                "description": "Bluebeam Summary",
                "url": "/groups/community_development/bluebeam/",
                "icon": "fas fa-file-alt",
            },
            {
                "id": "permits_inspections",
                "name": "Permits and Inspections",
                "description": "Permit and Inspections Trends and Summaries",
                "url": "/groups/community_development/permits_inspections/",
                "icon": "fa-solid fa-file-circle-check",
            },
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info(
            "Rendering Community Development dashboard with %d reports", len(reports)
        )

        return render_template(
            "groups/community_development/dashboard.html",
            title="Community Development Reports Dashboard",
            reports=reports,
        )

    except Exception as e:
        logger.error("Error rendering Community Development dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
