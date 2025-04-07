"""
Public Works Solid Waste Routes.

This module defines the routes for the Public Works Solid Waste reports blueprint.
These reports are embedded from Power BI during the transition to Python-based reports.
"""

import logging
from flask import render_template

from app.groups.public_works.solid_waste import bp

# Configure logger
logger = logging.getLogger(__name__)

# Power BI report configuration
SOLID_WASTE_REPORT = {
    "id": "solid_waste",
    "name": "Solid Waste Billing",
    "description": "Solid Waste Billing Data for Town Provided Waste Pickup",
    "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiOTM3OTcyNTEtZTY2Yi00MWE0LWI5YzEtYmFmMDc0N2I1NGFkIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=b4254b9017b9e7add9dd",
    "icon": "fa-solid fa-trash",
    "group": "Public Works",
}


@bp.route("/")
def index():
    """
    Render the Public Works Solid Waste report.

    Returns:
        str: Rendered HTML template.
    """
    try:
        logger.info("Rendering Public Works Solid Waste report")

        return render_template(
            "groups/public_works/solid_waste/index.html",
            title="Solid Waste Billing",
            report=SOLID_WASTE_REPORT,
            reports=[SOLID_WASTE_REPORT],  # For consistency with navigation tabs
        )

    except Exception as e:
        logger.error("Error rendering Public Works Solid Waste report: %s", str(e))
        return render_template("error.html", error=str(e))
