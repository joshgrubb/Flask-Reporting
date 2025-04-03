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

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.new_customer_accounts import routes  # noqa
