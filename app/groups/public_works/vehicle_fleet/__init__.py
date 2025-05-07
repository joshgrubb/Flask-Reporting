"""
Public Works Vehicle Fleet Report Blueprint.

This module defines the blueprint for the Vehicle Fleet report.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "vehicle_fleet",
    __name__,
    url_prefix="/vehicle_fleet",
    template_folder="../../../templates/groups/public_works/vehicle_fleet",
)

# Add report metadata
bp.report_metadata = {
    "id": "vehicle_fleet",
    "name": "Vehicle Fleet Dashboard",
    "description": "Vehicle Replacement Scores and GeoTab Alerts",
    "url": "/groups/public_works/vehicle_fleet/",
    "group_id": "public_works",
    "icon": "fa-solid fa-car",
}

# Import routes at the bottom to avoid circular imports
from app.groups.public_works.vehicle_fleet import routes  # noqa
