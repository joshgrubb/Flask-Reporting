"""
Finance ClearGov Report Blueprint.

This module defines the blueprint for the ClearGov reports.
These reports are embedded from ClearGov for budget visualization.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "cleargov",
    __name__,
    url_prefix="/cleargov",
    template_folder="../../../templates/groups/finance/cleargov",
)

# Add report metadata
bp.report_metadata = {
    "id": "cleargov",
    "name": "ClearGov Budget Visualizations",
    "description": "Interactive budget visualizations from ClearGov",
    "url": "/groups/finance/cleargov/",
    "group_id": "finance",
    "icon": "fa-solid fa-chart-pie",
}

# Import routes at the bottom to avoid circular imports
from app.groups.finance.cleargov import routes  # noqa
