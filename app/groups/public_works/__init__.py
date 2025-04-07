"""
Public Works Group Module.

This module defines the blueprint for the Public Works group.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "public_works",
    __name__,
    url_prefix="/public_works",
    template_folder="../../templates/groups/public_works",
)

# Import routes at the bottom to avoid circular imports
from app.groups.public_works import routes  # noqa

# Import and register report blueprints
from app.groups.public_works.solid_waste import bp as solid_waste_bp  # noqa
from app.groups.public_works.vehicle_fleet import bp as vehicle_fleet_bp  # noqa

# Register the report blueprints
bp.register_blueprint(solid_waste_bp)
bp.register_blueprint(vehicle_fleet_bp)
