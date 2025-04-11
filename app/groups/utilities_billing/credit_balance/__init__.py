"""
Credit Balance Report Blueprint.

This module defines the blueprint for the Credit Balance report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "credit_balance",
    __name__,
    url_prefix="/credit_balance",
    template_folder="../../../templates/groups/utilities_billing/credit_balance",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.credit_balance import routes  # noqa
