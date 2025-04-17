# app/groups/finance/routes.py (updated)
"""
Finance Module Routes.

This module defines routes for the main Finance dashboard.
"""

import logging
from flask import render_template

from app.groups.finance import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the Finance reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available reports
        reports = [
            {
                "id": "budget",
                "name": "Budget Dashboard",
                "description": "Trends and analysis Budget",
                "url": "/groups/finance/budget/",
                "icon": "fa-solid fa-file-invoice-dollar",
            },
            {
                "id": "cleargov",
                "name": "ClearGov Budget Visualizations",
                "description": "Interactive budget visualizations from ClearGov",
                "url": "/groups/finance/cleargov/",
                "icon": "fa-solid fa-chart-pie",
            },
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Finance dashboard with %d reports", len(reports))

        return render_template(
            "groups/finance/dashboard.html",
            title="Finance Reports Dashboard",
            reports=reports,
        )

    except Exception as e:
        logger.error("Error rendering Finance dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
