"""
Public Works Module Routes.

This module defines routes for the main Public Works dashboard.
"""

import logging
from flask import render_template

from app.groups.public_works import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the Public Works reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available reports
        reports = [
            {
                "id": "solid_waste",
                "name": "Solid Waste Billing",
                "description": "Solid Waste Billing Data for Town Provided Waste Pickup",
                "url": "/groups/public_works/solid_waste/",
                "icon": "fa-solid fa-trash",
            },
            {
                "id": "vehicle_fleet",
                "name": "Vehicle Fleet Dashboard",
                "description": "Vehicle Replacement Scores and GeoTab Alerts",
                "url": "/groups/public_works/vehicle_fleet/",
                "icon": "fa-solid fa-car",
            },
            {
                "id": "fleet_costs",
                "name": "Vehicle Fleet Costs",
                "description": "Vehicle Fleet costs by department and vehicle",
                "url": "/groups/public_works/fleet_costs/",
                "icon": "fa-solid fa-dollar-sign",
            },
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Public Works dashboard with %d reports", len(reports))

        return render_template(
            "groups/public_works/dashboard.html",
            title="Public Works Reports Dashboard",
            reports=reports,
        )

    except Exception as e:
        logger.error("Error rendering Public Works dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
