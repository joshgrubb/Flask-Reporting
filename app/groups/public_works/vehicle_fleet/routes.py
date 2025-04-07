"""
Public Works Vehicle Fleet Routes.

This module defines the routes for the Public Works Vehicle Fleet reports blueprint.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

import logging
from flask import render_template

from app.groups.public_works.vehicle_fleet import bp

# Configure logger
logger = logging.getLogger(__name__)

# Power BI report configuration
VEHICLE_FLEET_REPORT = {
    "id": "vehicle_fleet",
    "name": "Vehicle Fleet Dashboard",
    "description": "Vehicle Replacement Scores and GeoTab Alerts",
    "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiNTZjMTRiMjUtYWYzMS00ZjAxLTllMWItYmQ5OWNhMWZlYTE0IiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSection",
    "icon": "fa-solid fa-car",
    "group": "Public Works",
}


@bp.route("/")
def index():
    """
    Render the Public Works Vehicle Fleet report.

    Returns:
        str: Rendered HTML template.
    """
    try:
        logger.info("Rendering Public Works Vehicle Fleet report")

        return render_template(
            "groups/public_works/vehicle_fleet/index.html",
            title="Vehicle Fleet Dashboard",
            report=VEHICLE_FLEET_REPORT,
            reports=[VEHICLE_FLEET_REPORT],  # For consistency with navigation tabs
        )

    except Exception as e:
        logger.error("Error rendering Public Works Vehicle Fleet report: %s", str(e))
        return render_template("error.html", error=str(e))
