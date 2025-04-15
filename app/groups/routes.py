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
                "id": "community_development",
                "name": "Community Development",
                "description": "Reports for Engineering, Development Services, Inspections and Planning",
                "url": "/groups/community_development/",
                "icon": "fa-solid fa-file-circle-check",
                "enabled": True,  # Set to False if not yet implemented
            },
            {
                "id": "finance",
                "name": "Finance",
                "description": "Financial reports and budget analysis",
                "url": "/groups/finance/",
                "icon": "fa-solid fa-file-invoice-dollar",
                "enabled": True,  # Set to False if not yet implemented
            },
            {
                "id": "public_works",
                "name": "Public Works",
                "description": "Public Works reports on vehicles and solid waste",
                "url": "/groups/public_works/",
                "icon": "fa-solid fa-car",
                "enabled": True,  # Set to False if not yet implemented
            },
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
            {
                "id": "water_resources",
                "name": "Water Resources",
                "description": "Reports related to water resources",
                "url": "/groups/water_resources/",
                "icon": "fa-solid fa-water",
                "enabled": True,
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
