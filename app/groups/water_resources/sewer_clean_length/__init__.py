"""
Sewer Clean Length Report Blueprint.

This module defines the blueprint for the Sewer Clean Length report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "sewer_clean_length",
    __name__,
    url_prefix="/sewer_clean_length",
    template_folder="../../../templates/groups/water_resources/sewer_clean_length",
)

# Add report metadata
bp.report_metadata = {
    "id": "sewer_clean_length",
    "name": "Sewer Clean Length",
    "description": "View sanitary sewer cleaning lengths by work order",
    "url": "/groups/water_resources/sewer_clean_length/",
    "group_id": "water_resources",
    "icon": "fas fa-broom",
}

# Import routes at the bottom to avoid circular imports
from app.groups.water_resources.sewer_clean_length import routes  # noqa
