"""
Warehouse Audit Transactions Report Blueprint.

This module defines the blueprint for the Warehouse Audit Transactions report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "audit_transactions",
    __name__,
    url_prefix="/audit_transactions",
    template_folder="../../../templates/groups/warehouse/audit_transactions",
)

# Add report metadata
bp.report_metadata = {
    "id": "audit_transactions",
    "name": "Audit Transactions",
    "description": "View inventory audit transactions showing cost and quantity changes",
    "url": "/groups/warehouse/audit_transactions/",
    "group_id": "warehouse",
    "icon": "fas fa-file-invoice-dollar",
}

# Import routes at the bottom to avoid circular imports
from app.groups.warehouse.audit_transactions import routes  # noqa
