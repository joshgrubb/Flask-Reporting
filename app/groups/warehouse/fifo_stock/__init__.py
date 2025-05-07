"""
FIFO Stock Cost Report Blueprint.

This module defines the blueprint for the FIFO Stock Cost report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "fifo_stock",
    __name__,
    url_prefix="/fifo_stock",
    template_folder="../../../templates/groups/warehouse/fifo_stock",
)

# Add report metadata
bp.report_metadata = {
    "id": "fifo_stock",
    "name": "Inventory Cost Trends",
    "description": "View inventory items filtered by category with value and quantity analysis",
    "url": "/groups/warehouse/fifo_stock/",
    "group_id": "warehouse",
    "icon": "fas fa-boxes",
}

# Import routes at the bottom to avoid circular imports
from app.groups.warehouse.fifo_stock import routes  # noqa
