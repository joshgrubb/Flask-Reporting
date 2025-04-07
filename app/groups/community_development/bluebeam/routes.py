"""
Community Development Bluebeam Routes.

This module defines the routes for the Community Development Bluebeam reports blueprint.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

import logging
from flask import render_template

from app.groups.community_development.bluebeam import bp

# Configure logger
logger = logging.getLogger(__name__)

# Power BI report configuration
BLUEBEAM_REPORT = {
    "id": "bluebeam",
    "name": "Bluebeam Development Projects",
    "description": "Bluebeam Summary",
    "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiN2JlOTJmMDQtOThmZC00YWNlLWI3NTMtMWExYTBjNzdlNzIwIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSection",
    "icon": "fas fa-file-alt",
    "group": "Community Development",
}


@bp.route("/")
def index():
    """
    Render the Community Development Bluebeam report.

    Returns:
        str: Rendered HTML template.
    """
    try:
        logger.info("Rendering Community Development Bluebeam report")

        return render_template(
            "groups/community_development/bluebeam/index.html",
            title="Bluebeam Development Projects",
            report=BLUEBEAM_REPORT,
            reports=[BLUEBEAM_REPORT],  # For consistency with navigation tabs
        )

    except Exception as e:
        logger.error(
            "Error rendering Community Development Bluebeam report: %s", str(e)
        )
        return render_template("error.html", error=str(e))
