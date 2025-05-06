"""
Water Resources Module Routes.

This module defines routes for the main Water Resources dashboard.
"""

import logging
from flask import render_template

from app.groups.water_resources import bp
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
            {
                "id": "sewer_clean_length",
                "name": "Sewer Clean Length",
                "description": "View sanitary sewer cleaning lengths by work order",
                "url": "/groups/water_resources/sewer_clean_length/",
                "icon": "fas fa-broom",
            },
            {
                "id": "labor_requests",
                "name": "Labor Requests",
                "description": "View and analyze labor requests",
                "url": "/groups/water_resources/labor_requests/",
                "icon": "fas fa-hard-hat",
            },
            {
                "id": "work_order_comments",
                "name": "Work Order Comments Search",
                "description": "Search for specific text within work order comments",
                "url": "/groups/water_resources/work_order_comments/",
                "icon": "fas fa-search",
            },
            {
                "id": "work_order_details",
                "name": "Work Order Details",
                "description": "Search for specific work orders",
                "url": "/groups/water_resources/work_order_details/",
                "icon": "fas fa-search",
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
