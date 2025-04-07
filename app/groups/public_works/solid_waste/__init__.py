"""
Public Works Solid Waste Report Blueprint.

This module defines the blueprint for the Solid Waste report.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "solid_waste",
    __name__,
    url_prefix="/solid_waste",
    template_folder="../../../templates/groups/public_works/solid_waste",
)

# Import routes at the bottom to avoid circular imports
from app.groups.public_works.solid_waste import routes  # noqa
