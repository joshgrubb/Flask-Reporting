"""
Reports Module.

This module manages all report types (SSRS, PowerBI, etc.).
"""

from flask import Blueprint

bp = Blueprint(
    "reports", __name__, url_prefix="/reports", template_folder="../templates/reports"
)

# Import and register sub-blueprints
from app.reports.ssrs import bp as ssrs_bp  # noqa

# Register the report type blueprints
bp.register_blueprint(ssrs_bp)

# Import routes at the bottom to avoid circular imports
from app.reports import routes  # noqa
