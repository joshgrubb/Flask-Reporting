"""
Sewer Clean Length Report Blueprint.

This module defines the blueprint for the Sewer Clean Length report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "sewer_clean_length",
    __name__,
    url_prefix="/sewer_clean_length",
    template_folder="../../../templates/groups/water_resources/sewer_clean_length",
)

# Import routes at the bottom to avoid circular imports
from app.groups.water_resources.sewer_clean_length import routes  # noqa
