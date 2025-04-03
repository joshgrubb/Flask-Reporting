"""
Warehouse Module Routes.

This module defines routes for the main Warehouse dashboard.
"""

import logging
from flask import render_template, current_app

from app.groups.utilities_billing import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the Warehouse reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available reports
        reports = [
            {
                "id": "fifo_cost_wo",
                "name": "FIFO Work Order Costs",
                "description": "Report showing new customer account information",
                "url": "/groups/warehouse/fifo_cost_wo/",
            },
            
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Warehouse dashboard with %d reports", len(reports))

        return render_template(
            "warehouse/dashboard.html", title="Warehouse Reports Dashboard", reports=reports
        )

    except Exception as e:
        logger.error(f"Error rendering Warehouse dashboard: {str(e)}")
        return render_template("error.html", error=str(e))
