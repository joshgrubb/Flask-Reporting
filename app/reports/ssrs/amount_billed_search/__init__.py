"""
Amount Billed Search Report Blueprint.

This module defines the blueprint for the Amount Billed Search SSRS report conversion.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "amount_billed_search",
    __name__,
    url_prefix="/amount_billed_search",
    template_folder="../../../templates/ssrs/amount_billed_search",
)

# Import routes at the bottom to avoid circular imports
from app.reports.ssrs.amount_billed_search import routes  # noqa
