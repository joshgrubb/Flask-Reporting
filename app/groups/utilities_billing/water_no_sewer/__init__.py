"""
Water No Sewer Report Blueprint.

This module defines the blueprint for the Water No Sewer report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "water_no_sewer",
    __name__,
    url_prefix="/water_no_sewer",
    template_folder="../../../templates/groups/utilities_billing/water_no_sewer",
)

# Add report metadata
bp.report_metadata = {
    "id": "water_no_sewer",
    "name": "Water No Sewer",
    "description": "View accounts with water but no sewer service",
    "url": "/groups/utilities_billing/water_no_sewer/",
    "group_id": "utilities_billing",
    "icon": "fa-solid fa-glass-water",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.water_no_sewer import routes  # noqa
