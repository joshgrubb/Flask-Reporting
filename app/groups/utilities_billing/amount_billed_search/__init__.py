"""
Amount Billed Search Report Blueprint.

This module defines the blueprint for the Amount Billed Search report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "amount_billed_search",
    __name__,
    url_prefix="/amount_billed_search",
    template_folder="../../../templates/groups/amount_billed_search",
)

# Add report metadata
bp.report_metadata = {
    "id": "amount_billed_search",
    "name": "Amount Billed Search",
    "description": "Search for bill amounts in the system",
    "url": "/groups/utilities_billing/amount_billed_search/",
    "group_id": "utilities_billing",
    "icon": "fas fa-search-dollar",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.amount_billed_search import routes  # noqa
