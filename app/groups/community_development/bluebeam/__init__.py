"""
Community Development Bluebeam Report Blueprint.

This module defines the blueprint for the Bluebeam Development Projects report.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "bluebeam",
    __name__,
    url_prefix="/bluebeam",
    template_folder="../../../templates/groups/community_development/bluebeam",
)

# Import routes at the bottom to avoid circular imports
from app.groups.community_development.bluebeam import routes  # noqa
