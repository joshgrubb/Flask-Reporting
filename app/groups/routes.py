"""
Groups Module Routes.

This module defines routes for the main Groups dashboard.
"""

import logging
from flask import render_template
from app.core.report_registry import get_all_groups, get_group_reports

from app.groups import bp

# Configure logger
logger = logging.getLogger(__name__)


# app/groups/routes.py
@bp.route("/")
def index():
    """
    Render the main Groups dashboard.
    """
    try:
        # Use the registry instead of manually listing groups
        groups = get_all_groups()

        logger.info("Rendering Groups dashboard with %d groups", len(groups))

        return render_template(
            "groups/dashboard_base.html",
            title="Reports Dashboard",
            groups=groups,
        )
    except Exception as e:
        logger.error("Error rendering Groups dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
