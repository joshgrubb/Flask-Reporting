"""
Reports Module Routes.

This module defines routes for the main reports dashboard.
"""

import logging
from flask import render_template

from app.reports import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/", methods=["GET"])
def index():
    """
    Render the main reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available report types
        report_types = [
            {
                "id": "ssrs",
                "name": "SSRS Reports",
                "description": "SQL Server Reporting Services converted reports",
                "url": "/reports/ssrs/",
            },
            {
                "id": "powerbi",
                "name": "Power BI Reports",
                "description": "Power BI converted reports",
                "url": "/reports/powerbi/",
                "enabled": False,  # Not yet implemented
            },
        ]

        return render_template(
            "dashboard.html", title="Reports Dashboard", report_types=report_types
        )

    except Exception as e:
        logger.error(f"Error rendering reports dashboard: {str(e)}")
        return render_template("error.html", error=str(e))
