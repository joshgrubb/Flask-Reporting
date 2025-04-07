"""
Groups Module.

This module organizes all report groups (Utilities Billing, Finance, etc.).
"""

from flask import Blueprint

bp = Blueprint(
    "groups", __name__, url_prefix="/groups", template_folder="../templates/groups"
)

# Import routes at the bottom to avoid circular imports
from app.groups import routes  # noqa

# Import and register sub-blueprints
from app.groups.utilities_billing import bp as utilities_billing_bp  # noqa
from app.groups.warehouse import bp as warehouse_bp  # noqa
from app.groups.powerbi import bp as powerbi_bp  # noqa  # Add this line

# Register the group blueprints
bp.register_blueprint(utilities_billing_bp)

bp.register_blueprint(warehouse_bp)

bp.register_blueprint(powerbi_bp)  # Add this line
