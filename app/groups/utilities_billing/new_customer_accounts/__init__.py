"""
New Customer Accounts Report Blueprint.

This module defines the blueprint for the New Customer Accounts report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "new_customer_accounts",
    __name__,
    url_prefix="/new_customer_accounts",
    template_folder="../../../templates/groups/utilities_billing/new_customer_accounts",
)

# Add report metadata
bp.report_metadata = {
    "id": "new_customer_accounts",
    "name": "New Customer Accounts",
    "description": "Report showing new customer account information",
    "url": "/groups/utilities_billing/new_customer_accounts/",
    "group_id": "utilities_billing",
    "icon": "fas fa-user-plus",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.new_customer_accounts import routes  # noqa
