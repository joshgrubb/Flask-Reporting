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

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.high_balance import routes  # noqa
