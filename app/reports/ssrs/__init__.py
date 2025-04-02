"""
SSRS Reports Module.

This module handles all SSRS report conversions.
"""

from flask import Blueprint

# Create the SSRS blueprint
bp = Blueprint(
    "ssrs", __name__, url_prefix="/ssrs", template_folder="../../templates/ssrs"
)

# Import routes at the bottom to avoid circular imports
from app.reports.ssrs import routes  # noqa

# Import and register new_customer_accounts blueprint
from app.reports.ssrs.new_customer_accounts import bp as new_customer_accounts_bp

bp.register_blueprint(new_customer_accounts_bp)

# Import and register no_occupant_list_for_moveouts blueprint
from app.reports.ssrs.no_occupant_list_for_moveouts import (
    bp as no_occupant_list_for_moveouts_bp,
)

bp.register_blueprint(no_occupant_list_for_moveouts_bp)
