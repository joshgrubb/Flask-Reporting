"""
VFLEX Report Blueprint.

This module defines the blueprint for the VFLEX for Sensus report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "vflex",
    __name__,
    url_prefix="/vflex",
    template_folder="../../../templates/groups/utilities_billing/vflex",
)

# Add report metadata
bp.report_metadata = {
    "id": "vflex",
    "name": "VFLEX for Sensus",
    "description": "VFLEX file to upload to Sensus to update customer data.",
    "url": "/groups/utilities_billing/vflex/",
    "group_id": "utilities_billing",
    "icon": "fa-solid fa-users",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.vflex import routes  # noqa
