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

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.dollar_search import routes  # noqa
