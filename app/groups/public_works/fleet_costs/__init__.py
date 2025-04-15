# app/groups/public_works/fleet_costs/__init__.py
"""
Fleet Costs Report Blueprint.

This module defines the blueprint for the Fleet Costs report,
which tracks and analyzes vehicle maintenance costs.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "fleet_costs",
    __name__,
    url_prefix="/fleet_costs",
    template_folder="../../../templates/groups/public_works/fleet_costs",
)

# Import routes at the bottom to avoid circular imports
from app.groups.public_works.fleet_costs import routes  # noqa
