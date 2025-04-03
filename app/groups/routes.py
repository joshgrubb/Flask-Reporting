"""
Groups Module Routes.

This module defines routes for the main Groups dashboard.
"""

import logging
from flask import render_template

from app.groups import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the main Groups dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available groups
        groups = [
            {
                "id": "utilities_billing",
                "name": "Utilities Billing",
                "description": "Reports related to utility billing, accounts, and services",
                "url": "/groups/utilities_billing/",
                "icon": "fas fa-file-invoice-dollar",
                "enabled": True,
            },
            {
                "id": "warehouse",
                "name": "Warehouse",
                "description": "Reports related to inventory, work orders, and stock management",
                "url": "/groups/warehouse/",
                "icon": "fas fa-warehouse",
                "enabled": True,
            },
            # Additional groups can be added here
            {
                "id": "finance",
                "name": "Finance",
                "description": "Financial reports and budget analysis",
                "url": "/groups/finance/",
                "icon": "fas fa-chart-line",
                "enabled": False,  # Set to False if not yet implemented
            },
            {
                "id": "hr",
                "name": "Human Resources",
                "description": "Employee and personnel management reports",
                "url": "/groups/hr/",
                "icon": "fas fa-users",
                "enabled": False,  # Set to False if not yet implemented
            },
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Groups dashboard with %d groups", len(groups))

        return render_template(
            "groups/dashboard.html", title="Reports Dashboard", groups=groups
        )

    except Exception as e:
        logger.error("Error rendering Groups dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
