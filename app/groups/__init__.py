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
from app.groups.public_works import bp as public_works_bp  # noqa
from app.groups.finance import bp as finance_bp  # noqa
from app.groups.community_development import bp as community_development_bp  # noqa

# Register the group blueprints
bp.register_blueprint(utilities_billing_bp)
bp.register_blueprint(warehouse_bp)
bp.register_blueprint(public_works_bp)
bp.register_blueprint(finance_bp)
bp.register_blueprint(community_development_bp)
