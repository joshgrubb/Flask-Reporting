# app/groups/water_resources/__init__.py
"""
Water Resources Group Module.

This module defines the blueprint for the Water Resources group.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "water_resources",
    __name__,
    url_prefix="/water_resources",
    template_folder="../../templates/groups/water_resources",
)

# Import routes at the bottom to avoid circular imports
from app.groups.water_resources import routes  # noqa

# Import and register hydrant_history blueprint
from app.groups.water_resources.hydrant_history import bp as hydrant_history_bp  # noqa


bp.register_blueprint(hydrant_history_bp)
