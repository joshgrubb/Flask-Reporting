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


@bp.route("/")
def index():
    """
    Render the main Groups dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # Get all registered groups from the registry
        groups = get_all_groups()

        # Log the number of groups for debugging
        logger.info("Rendering Groups dashboard with %d groups", len(groups))

        return render_template(
            "groups/index.html",  # Use a specific template for the main dashboard
            title="Reports Dashboard",
            groups=groups,
        )
    except Exception as e:
        logger.error("Error rendering Groups dashboard: %s", str(e))
        return render_template("error.html", error=str(e))
