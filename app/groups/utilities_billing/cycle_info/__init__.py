"""
Cycle Info Report Blueprint.

This module defines the blueprint for the Cycle Info report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "cycle_info",
    __name__,
    url_prefix="/cycle_info",
    template_folder="../../../templates/groups/utilities_billing/cycle_info",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.cycle_info import routes  # noqa
"""
Cycle Info Report Blueprint.

This module defines the blueprint for the Cycle Info report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "cycle_info",
    __name__,
    url_prefix="/cycle_info",
    template_folder="../../../templates/groups/utilities_billing/cycle_info",
)

# Add report metadata
bp.report_metadata = {
    "id": "cycle_info",
    "name": "Cycle Info Report",
    "description": "View account information organized by billing cycle",
    "url": "/groups/utilities_billing/cycle_info/",
    "group_id": "utilities_billing",
    "icon": "fas fa-sync-alt",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.cycle_info import routes  # noqa
