# app/groups/warehouse/routes.py (updated)
"""
Warehouse Module Routes.

This module defines routes for the main Warehouse dashboard.
"""

import logging
from flask import render_template

from app.groups.warehouse import bp

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
                "description": "Report showing work order costs using FIFO inventory method",
                "url": "/groups/warehouse/fifo_cost_wo/",
                "icon": "fas fa-clipboard-list",
            },
            {
                "id": "fifo_stock",
                "name": "FIFO Stock Cost",
                "description": "View inventory items filtered by category with value and quantity analysis",
                "url": "/groups/warehouse/fifo_stock/",
                "icon": "fas fa-boxes",
            },
            {
                "id": "audit_transactions",
                "name": "Audit Transactions",
                "description": "View inventory audit transactions showing cost and quantity changes",
                "url": "/groups/warehouse/audit_transactions/",
                "icon": "fas fa-file-invoice-dollar",
            },
            {
                "id": "stock_by_storeroom",
                "name": "Stock By Storeroom",
                "description": "View inventory items by storeroom location with min/max quantity analysis",
                "url": "/groups/warehouse/stock_by_storeroom/",
                "icon": "fas fa-warehouse",
            },
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Warehouse dashboard with %d reports", len(reports))

        return render_template(
            "groups/warehouse/dashboard.html",
            title="Warehouse Reports",
            reports=reports,
        )

    except Exception as e:
        logger.error("Error rendering Warehouse dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
