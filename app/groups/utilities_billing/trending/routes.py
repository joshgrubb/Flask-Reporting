"""
Utilities Billing Trending Routes.

This module defines the routes for the Utilities Billing Trending reports blueprint.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

import logging
from flask import render_template

from app.groups.utilities_billing.trending import bp

# Configure logger
logger = logging.getLogger(__name__)

# Power BI report configuration
UTILITY_DASHBOARD_REPORT = {
    "id": "utility_dashboard",
    "name": "Utility Billing Dashboard",
    "description": "Overview of utility billing metrics and KPIs",
    "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiN2ZkZTU0YzYtMDg2NC00MDFkLTgwY2MtMWE3N2Q3MjhiY2MxIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=90ec2537a310d208e68c",
    "icon": "fas fa-file-invoice-dollar",
    "group": "Utilities Billing",
}


@bp.route("/")
def index():
    """
    Render the Utilities Billing Trending report.

    Returns:
        str: Rendered HTML template.
    """
    try:
        logger.info("Rendering Utilities Billing Trending report")

        return render_template(
            "groups/utilities_billing/trending/index.html",
            title="Utility Billing Dashboard",
            report=UTILITY_DASHBOARD_REPORT,
            reports=[UTILITY_DASHBOARD_REPORT],  # For consistency with navigation tabs
        )

    except Exception as e:
        logger.error("Error rendering Utilities Billing Trending report: %s", str(e))
        return render_template("error.html", error=str(e))
