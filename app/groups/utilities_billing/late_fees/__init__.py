"""
Late Fees Report Blueprint.

This module defines the blueprint for the Late Fees report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "late_fees",
    __name__,
    url_prefix="/late_fees",
    template_folder="../../../templates/groups/utilities_billing/late_fees",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.late_fees import routes  # noqa
