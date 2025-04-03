"""
Warehouse Group Module.

This module defines the blueprint for the Warehouse group.
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
# Import the report blueprints after the main blueprint has been created
# to avoid circular imports
from app.groups.warehouse.fifo_cost_wo import bp as fifo_cost_wo_bp  # noqa

# Register the report blueprints
bp.register_blueprint(fifo_cost_wo_bp)
