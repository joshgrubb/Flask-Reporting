"""
Finance Budget Routes.

This module defines the routes for the Finance Budget reports blueprint.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

import logging
from flask import render_template

from app.groups.finance.budget import bp

# Configure logger
logger = logging.getLogger(__name__)

# Power BI report configuration
BUDGET_REPORT = {
    "id": "budget",
    "name": "Budget Dashboard",
    "description": "Trends and analysis Budget",
    "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiZjI2NTU5OWMtZmUwMy00MWExLTg0OWItMDQwMjUxZWMwZDdjIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSectionc4c9ec86076a26b5930d",
    "icon": "fa-solid fa-file-invoice-dollar",
    "group": "Finance",
}


@bp.route("/")
def index():
    """
    Render the Finance Budget report.

    Returns:
        str: Rendered HTML template.
    """
    try:
        logger.info("Rendering Finance Budget report")

        return render_template(
            "groups/finance/budget/index.html",
            title="Budget Dashboard",
            report=BUDGET_REPORT,
            reports=[BUDGET_REPORT],  # For consistency with navigation tabs
        )

    except Exception as e:
        logger.error("Error rendering Finance Budget report: %s", str(e))
        return render_template("error.html", error=str(e))
