"""
Accounts No Garbage Report Blueprint.

This module defines the blueprint for the Accounts No Garbage report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "accounts_no_garbage",
    __name__,
    url_prefix="/accounts_no_garbage",
    template_folder="../../../templates/groups/utilities_billing/accounts_no_garbage",
)

# Add report metadata
bp.report_metadata = {
    "id": "accounts_no_garbage",
    "name": "Accounts Without Garbage Service",
    "description": "Report showing residential accounts without garbage service",
    "url": "/groups/utilities_billing/accounts_no_garbage/",
    "group_id": "utilities_billing",
    "icon": "fa-solid fa-trash",
}

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.accounts_no_garbage import routes  # noqa
