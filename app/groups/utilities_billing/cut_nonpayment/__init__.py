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

# Add report metadata
bp.report_metadata = {
    "id": "cut_nonpayment",
    "name": "Cut for Nonpayment",
    "description": "View accounts being cut for nonpayment",
    "url": "/groups/utilities_billing/cut_nonpayment/",
    "group_id": "utilities_billing",
    "icon": "fas fa-cut",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.cut_nonpayment import routes  # noqa
