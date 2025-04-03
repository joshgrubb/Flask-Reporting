"""
Utilities Billing Group Module.

This module defines the blueprint for the Utilities Billing group.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "warehouse",
    __name__,
    url_prefix="/warehouse",
    template_folder="../../templates/groups/warehouse",
)

# Import routes at the bottom to avoid circular imports
from app.groups.warehouse import routes  # noqa

# Import and register report blueprints
from app.groups.warehouse.fifo_cost_wo import (
    bp as fifo_cost_wo_bp,
)  # noqa
