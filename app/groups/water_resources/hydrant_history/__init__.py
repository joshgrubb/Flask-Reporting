# app/groups/water_resources/hydrant_history/__init__.py
"""
Hydrant History Report Blueprint.

This module defines the blueprint for the Hydrant History report.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "hydrant_history",
    __name__,
    url_prefix="/hydrant_history",
    template_folder="../../../templates/groups/water_resources/hydrant_history",
)

# Import routes at the bottom to avoid circular imports
from app.groups.water_resources.hydrant_history import routes  # noqa
