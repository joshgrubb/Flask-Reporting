"""
Community Development Permits & Inspections Report Blueprint.

This module defines the blueprint for the Permits & Inspections report.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "permits_inspections",
    __name__,
    url_prefix="/permits_inspections",
    template_folder="../../../templates/groups/community_development/permits_inspections",
)

# Import routes at the bottom to avoid circular imports
from app.groups.community_development.permits_inspections import routes  # noqa
