"""
Community Development Permits & Inspections Routes.

This module defines the routes for the Community Development Permits & Inspections reports blueprint.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

import logging
from flask import render_template

from app.groups.community_development.permits_inspections import bp

# Configure logger
logger = logging.getLogger(__name__)

# Power BI report configuration
PERMITS_INSPECTIONS_REPORT = {
    "id": "permits_inspections",
    "name": "Permits and Inspections",
    "description": "Permit and Inspections Trends and Summaries",
    "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiNzI0MmM5ZTYtM2E3NC00MDJlLWE5NWYtODAzMDk0ZmIzYmZlIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSectionbe6c43737b1fd78bdffc",
    "icon": "fa-solid fa-file-circle-check",
    "group": "Community Development",
}


@bp.route("/")
def index():
    """
    Render the Community Development Permits & Inspections report.

    Returns:
        str: Rendered HTML template.
    """
    try:
        logger.info("Rendering Community Development Permits & Inspections report")

        return render_template(
            "groups/community_development/permits_inspections/index.html",
            title="Permits and Inspections",
            report=PERMITS_INSPECTIONS_REPORT,
            reports=[
                PERMITS_INSPECTIONS_REPORT
            ],  # For consistency with navigation tabs
        )

    except Exception as e:
        logger.error(
            "Error rendering Community Development Permits & Inspections report: %s",
            str(e),
        )
        return render_template("error.html", error=str(e))
