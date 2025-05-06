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

# Import and register sewer_clean_length blueprint
from app.groups.water_resources.sewer_clean_length import (
    bp as sewer_clean_length_bp,
)  # noqa

bp.register_blueprint(hydrant_history_bp)
bp.register_blueprint(sewer_clean_length_bp)
