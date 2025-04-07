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

# Import routes at the bottom to avoid circular imports
from app.groups.public_works.vehicle_fleet import routes  # noqa
