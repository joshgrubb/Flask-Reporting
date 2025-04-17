# app/groups/finance/__init__.py (updated)
"""
Finance Group Module.

This module defines the blueprint for the Finance group.
"""

from flask import Blueprint

# Create the blueprint
bp = Blueprint(
    "finance",
    __name__,
    url_prefix="/finance",
    template_folder="../../templates/groups/finance",
)

# Import routes at the bottom to avoid circular imports
from app.groups.finance import routes  # noqa

# Import and register report blueprints
from app.groups.finance.budget import bp as budget_bp  # noqa
from app.groups.finance.cleargov import bp as cleargov_bp  # noqa

# Register the report blueprints
bp.register_blueprint(budget_bp)
bp.register_blueprint(cleargov_bp)
