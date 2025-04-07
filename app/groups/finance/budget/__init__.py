"""
Finance Budget Report Blueprint.

This module defines the blueprint for the Budget report.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "budget",
    __name__,
    url_prefix="/budget",
    template_folder="../../../templates/groups/finance/budget",
)

# Import routes at the bottom to avoid circular imports
from app.groups.finance.budget import routes  # noqa
