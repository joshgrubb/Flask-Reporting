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

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.cash_only_accounts import routes  # noqa
