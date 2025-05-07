"""
Utilities Billing Trending Reports Blueprint.

This module defines the blueprint for the Utilities Billing Trending reports.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "trending",
    __name__,
    url_prefix="/trending",
    template_folder="../../../templates/groups/utilities_billing/trending",
)

# Add report metadata
bp.report_metadata = {
    "id": "utility_dashboard",
    "name": "Utility Billing Dashboard",
    "description": "Overview of utility billing metrics and KPIs",
    "url": "/groups/utilities_billing/trending/",
    "group_id": "utilities_billing",
    "icon": "fa-solid fa-chart-column",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.trending import routes  # noqa
