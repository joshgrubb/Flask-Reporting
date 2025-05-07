"""
Late Fees Report Blueprint.

This module defines the blueprint for the Late Fees report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "late_fees",
    __name__,
    url_prefix="/late_fees",
    template_folder="../../../templates/groups/utilities_billing/late_fees",
)

# Add report metadata
bp.report_metadata = {
    "id": "late_fees",
    "name": "Late Fees Report",
    "description": "View accounts with a late fee",
    "url": "/groups/utilities_billing/late_fees/",
    "group_id": "utilities_billing",
    "icon": "fa-solid fa-calendar",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.late_fees import routes  # noqa
