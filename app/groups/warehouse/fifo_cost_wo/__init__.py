"""
FIFO Work Order Cost Report Blueprint.

This module defines the blueprint for the FIFO Work Order Cost report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "fifo_cost_wo",
    __name__,
    url_prefix="/fifo_cost_wo",
    template_folder="../../../templates/groups/warehouse/fifo_cost_wo",
)

# Import routes at the bottom to avoid circular imports
from app.groups.warehouse.fifo_cost_wo import routes  # noqa
