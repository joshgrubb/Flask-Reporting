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

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.amount_billed_search import routes  # noqa
