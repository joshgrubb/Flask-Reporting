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
