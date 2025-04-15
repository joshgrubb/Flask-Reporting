"""
Work Order Counts Report Blueprint.

This module defines the blueprint for the Work Order Counts report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "work_order_counts",
    __name__,
    url_prefix="/work_order_counts",
    template_folder="../../../templates/groups/utilities_billing/work_order_counts",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.work_order_counts import routes  # noqa
