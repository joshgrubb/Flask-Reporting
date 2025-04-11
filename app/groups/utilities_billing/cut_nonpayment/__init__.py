"""
Cut for Nonpayment Report Blueprint.

This module defines the blueprint for the Cut for Nonpayment report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "cut_nonpayment",
    __name__,
    url_prefix="/cut_nonpayment",
    template_folder="../../../templates/groups/utilities_billing/cut_nonpayment",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.cut_nonpayment import routes  # noqa
