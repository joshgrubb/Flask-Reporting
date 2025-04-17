# app/groups/finance/cleargov/__init__.py
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

# Import routes at the bottom to avoid circular imports
from app.groups.finance.cleargov import routes  # noqa
