"""
No Occupant List for Moveouts Report Blueprint.

This module defines the blueprint for the No Occupant List for Moveouts report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "no_occupant_list_for_moveouts",
    __name__,
    url_prefix="/no_occupant_list_for_moveouts",
    template_folder="../../../templates/groups/utilities_billing/no_occupant_list_for_moveouts",
)

# Add report metadata
bp.report_metadata = {
    "id": "no_occupant_list_for_moveouts",
    "name": "No Occupant List for Moveouts",
    "description": "Report showing addresses with moveouts that have no new occupants",
    "url": "/groups/utilities_billing/no_occupant_list_for_moveouts/",
    "group_id": "utilities_billing",
    "icon": "fa-solid fa-building-circle-arrow-right",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.no_occupant_list_for_moveouts import routes  # noqa
