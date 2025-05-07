"""
Hydrant History Report Blueprint.

This module defines the blueprint for the Hydrant History report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "hydrant_history",
    __name__,
    url_prefix="/hydrant_history",
    template_folder="../../../templates/groups/water_resources/hydrant_history",
)

# Add report metadata
bp.report_metadata = {
    "id": "hydrant_history",
    "name": "Hydrant History",
    "description": "View hydrant inspection and work order history",
    "url": "/groups/water_resources/hydrant_history/",
    "group_id": "water_resources",
    "icon": "fas fa-history",
}

# Import routes at the bottom to avoid circular imports
from app.groups.water_resources.hydrant_history import routes  # noqa
