"""
Public Works Module Routes.

This module defines routes for the main Public Works dashboard.
"""

import logging
from flask import render_template

from app.groups.public_works import bp
from app.shared.labor_requests import register_labor_requests_routes
from app.shared.work_order_comments import register_work_order_comments_routes
from app.shared.work_order_details import register_work_order_details_routes

# Register shared labor requests routes with this blueprint
register_labor_requests_routes(bp)

# Register shared work order comments routes with this blueprint
register_work_order_comments_routes(bp)

register_work_order_details_routes(bp)

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
                "name": "Solid Waste",
                "description": "View solid waste collection analytics",
                "url": "/groups/public_works/solid_waste/",
                "icon": "fas fa-trash",
            },
            {
                "id": "vehicle_fleet",
                "name": "Vehicle Fleet",
                "description": "Monitor vehicle fleet metrics",
                "url": "/groups/public_works/vehicle_fleet/",
                "icon": "fas fa-car",
            },
            {
                "id": "fleet_costs",
                "name": "Fleet Costs",
                "description": "Analyze vehicle maintenance costs",
                "url": "/groups/public_works/fleet_costs/",
                "icon": "fas fa-dollar-sign",
            },
            {
                "id": "labor_requests",
                "name": "Labor Requests",
                "description": "View and analyze labor requests",
                "url": "/groups/public_works/labor_requests/",
                "icon": "fas fa-hard-hat",
            },
            {
                "id": "work_order_comments",
                "name": "Work Order Comments Search",
                "description": "Search for specific text within work order comments",
                "url": "/groups/public_works/work_order_comments/",
                "icon": "fas fa-search",
            },
            {
                "id": "work_order_search",
                "name": "Work Order Search",
                "description": "Search for specific a work order",
                "url": "/groups/public_works/work_orders/search",
                "icon": "fas fa-search",
            },
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Public Works dashboard with %d reports", len(reports))

        return render_template(
            "groups/public_works/dashboard.html",
            title="Public Works Reports",
            reports=reports,
        )

    except Exception as e:
        logger.error("Error rendering Public Works dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
