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

# Add report metadata
bp.report_metadata = {
    "id": "fleet_costs",
    "name": "Fleet Costs",
    "description": "Analyze vehicle maintenance costs",
    "url": "/groups/public_works/fleet_costs/",
    "group_id": "public_works",
    "icon": "fas fa-dollar-sign",
}

# Import routes at the bottom to avoid circular imports
from app.groups.public_works.fleet_costs import routes  # noqa
