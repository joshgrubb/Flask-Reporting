"""
Stock By Storeroom Report Blueprint.

This module defines the blueprint for the Stock By Storeroom report
which displays inventory items by storeroom location.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "stock_by_storeroom",
    __name__,
    url_prefix="/stock_by_storeroom",
    template_folder="../../../templates/groups/warehouse/stock_by_storeroom",
)

# Add report metadata
bp.report_metadata = {
    "id": "stock_by_storeroom",
    "name": "Stock By Storeroom",
    "description": "View inventory items by storeroom location with min/max quantity analysis",
    "url": "/groups/warehouse/stock_by_storeroom/",
    "group_id": "warehouse",
    "icon": "fas fa-warehouse",
}

# Import routes at the bottom to avoid circular imports
from app.groups.warehouse.stock_by_storeroom import routes  # noqa
