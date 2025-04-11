# app/groups/utilities_billing/vflex/__init__.py
"""
VFLEX Report Blueprint.

This module defines the blueprint for the VFLEX for Sensus report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "vflex",
    __name__,
    url_prefix="/vflex",
    template_folder="../../../templates/groups/utilities_billing/vflex",
)

# Import routes at the bottom to avoid circular imports
from app.groups.utilities_billing.vflex import routes  # noqa
