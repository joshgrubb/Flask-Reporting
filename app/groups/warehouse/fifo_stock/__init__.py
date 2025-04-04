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

# Import routes at the bottom to avoid circular imports
from app.groups.warehouse.fifo_stock import routes  # noqa
