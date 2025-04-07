"""
Power BI Integration Blueprint.

This module defines the blueprint for embedding Power BI reports.
It serves as a transition tool while migrating from Power BI to Python-based reports.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "powerbi",
    __name__,
    url_prefix="/powerbi",
    template_folder="../../templates/groups/powerbi",
)

# Import routes at the bottom to avoid circular imports
from app.groups.powerbi import routes  # noqa
