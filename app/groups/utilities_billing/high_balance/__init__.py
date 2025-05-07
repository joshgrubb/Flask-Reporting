"""
High Balance Report Blueprint.

This module defines the blueprint for the High Balance report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "high_balance",
    __name__,
    url_prefix="/high_balance",
    template_folder="../../../templates/groups/utilities_billing/high_balance",
)

# Add report metadata
bp.report_metadata = {
    "id": "high_balance",
    "name": "High Balance Report",
    "description": "View accounts with a high balance",
    "url": "/groups/utilities_billing/high_balance/",
    "group_id": "utilities_billing",
    "icon": "fas fa-dollar-sign",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.high_balance import routes  # noqa
