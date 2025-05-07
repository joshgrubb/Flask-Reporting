"""
Dollar Search Report Blueprint.

This module defines the blueprint for the Dollar Search report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "dollar_search",
    __name__,
    url_prefix="/dollar_search",
    template_folder="../../../templates/groups/utilities_billing/dollar_search",
)

# Add report metadata
bp.report_metadata = {
    "id": "dollar_search",
    "name": "Dollar Search",
    "description": "Search for transactions by specific dollar amount across all payment sources",
    "url": "/groups/utilities_billing/dollar_search/",
    "group_id": "utilities_billing",
    "icon": "fas fa-dollar-sign",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.dollar_search import routes  # noqa
