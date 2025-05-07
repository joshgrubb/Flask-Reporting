"""
Cash Only Accounts Report Blueprint.

This module defines the blueprint for the Cash Only Accounts report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "cash_only_accounts",
    __name__,
    url_prefix="/cash_only_accounts",
    template_folder="../../../templates/groups/utilities_billing/cash_only_accounts",
)

# Add report metadata
bp.report_metadata = {
    "id": "cash_only_accounts",
    "name": "Cash Only Accounts",
    "description": "Utility accounts restricted to cash only, no checks",
    "url": "/groups/utilities_billing/cash_only_accounts/",
    "group_id": "utilities_billing",
    "icon": "fa-solid fa-money-bill-1",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.cash_only_accounts import routes  # noqa
