"""
Community Development Group Module.

This module defines the blueprint for the Community Development group.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "community_development",
    __name__,
    url_prefix="/community_development",
    template_folder="../../templates/groups/community_development",
)

# Import routes at the bottom to avoid circular imports
from app.groups.community_development import routes  # noqa

# Import and register report blueprints
from app.groups.community_development.bluebeam import bp as bluebeam_bp  # noqa
from app.groups.community_development.permits_inspections import (
    bp as permits_inspections_bp,
)  # noqa

# Register the report blueprints
bp.register_blueprint(bluebeam_bp)
bp.register_blueprint(permits_inspections_bp)
