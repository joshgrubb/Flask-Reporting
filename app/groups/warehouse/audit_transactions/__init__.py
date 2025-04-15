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

# Import routes at the bottom to avoid circular imports
from app.groups.warehouse.audit_transactions import routes  # noqa
