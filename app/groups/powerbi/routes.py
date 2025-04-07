"""
Power BI Integration Routes.

This module defines routes for embedding Power BI reports within the application.
It serves as a transition tool while moving from Power BI to Python-based reports.
"""

import logging
from flask import render_template, request, jsonify

from app.groups.powerbi import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the main Power BI reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available Power BI reports
        # This could be stored in a database or config file in production
        reports = [
            {
                "id": "utility_dashboard",
                "name": "Utility Billing Dashboard",
                "description": "Overview of utility billing metrics and KPIs",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiN2ZkZTU0YzYtMDg2NC00MDFkLTgwY2MtMWE3N2Q3MjhiY2MxIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=90ec2537a310d208e68c",
                "icon": "fas fa-file-invoice-dollar",
                "group": "Utilities Billing",
            },
            {
                "id": "solid_waste",
                "name": "Solid Waste Billing",
                "description": "Solid Waste Billing Data for Town Provided Waste Pickup",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiOTM3OTcyNTEtZTY2Yi00MWE0LWI5YzEtYmFmMDc0N2I1NGFkIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=b4254b9017b9e7add9dd",
                "icon": "fa-solid fa-trash",
                "group": "Public Works",
            },
            {
                "id": "vehicle_fleet",
                "name": "Vehicle Fleet Dashboard",
                "description": "Vehicle Replacement Scores and GeoTab Alerts",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiNTZjMTRiMjUtYWYzMS00ZjAxLTllMWItYmQ5OWNhMWZlYTE0IiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSection",
                "icon": "fa-solid fa-car",
                "group": "Public Works",
            },
            {
                "id": "budget",
                "name": "Budget Dashboard",
                "description": "Trends and analysis Budget",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiZjI2NTU5OWMtZmUwMy00MWExLTg0OWItMDQwMjUxZWMwZDdjIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSectionc4c9ec86076a26b5930d",
                "icon": "fa-solid fa-file-invoice-dollar",
                "group": "Finance",
            },
            {
                "id": "bluebeam",
                "name": "Bluebeam Development Projects",
                "description": "Bluebeam Summary",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiN2JlOTJmMDQtOThmZC00YWNlLWI3NTMtMWExYTBjNzdlNzIwIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSection",
                "icon": "fas fa-file-alt",
                "group": "Community Development",
            },
            {
                "id": "permits_inspections",
                "name": "Permits and Inspections",
                "description": "Permit and Inspections Trends and Summaries",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiNzI0MmM5ZTYtM2E3NC00MDJlLWE5NWYtODAzMDk0ZmIzYmZlIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSectionbe6c43737b1fd78bdffc",
                "icon": "fa-solid fa-file-circle-check",
                "group": "Community Development",
            },
        ]

        # Group reports by their category
        grouped_reports = {}
        for report in reports:
            group = report["group"]
            if group not in grouped_reports:
                grouped_reports[group] = []
            grouped_reports[group].append(report)

        # Log that we're rendering the dashboard
        logger.info(
            "Rendering Power BI reports dashboard with %d reports", len(reports)
        )

        return render_template(
            "groups/powerbi/dashboard.html",
            title="Power BI Reports Dashboard",
            reports=reports,
            grouped_reports=grouped_reports,
        )

    except Exception as e:
        logger.error("Error rendering Power BI dashboard: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/embed/<report_id>")
def embed_report(report_id):
    """
    Render a specific Power BI report.

    Args:
        report_id (str): The ID of the report to embed.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available Power BI reports
        # This should match the list in the index route
        reports = [
            {
                "id": "utility_dashboard",
                "name": "Utility Billing Dashboard",
                "description": "Overview of utility billing metrics and KPIs",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiN2ZkZTU0YzYtMDg2NC00MDFkLTgwY2MtMWE3N2Q3MjhiY2MxIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=90ec2537a310d208e68c",
                "icon": "fas fa-file-invoice-dollar",
                "group": "Utilities Billing",
            },
            {
                "id": "solid_waste",
                "name": "Solid Waste Billing",
                "description": "Solid Waste Billing Data for Town Provided Waste Pickup",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiOTM3OTcyNTEtZTY2Yi00MWE0LWI5YzEtYmFmMDc0N2I1NGFkIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=b4254b9017b9e7add9dd",
                "icon": "fa-solid fa-trash",
                "group": "Public Works",
            },
            {
                "id": "vehicle_fleet",
                "name": "Vehicle Fleet Dashboard",
                "description": "Vehicle Replacement Scores and GeoTab Alerts",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiNTZjMTRiMjUtYWYzMS00ZjAxLTllMWItYmQ5OWNhMWZlYTE0IiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSection",
                "icon": "fa-solid fa-car",
                "group": "Public Works",
            },
            {
                "id": "budget",
                "name": "Budget Dashboard",
                "description": "Trends and analysis Budget",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiZjI2NTU5OWMtZmUwMy00MWExLTg0OWItMDQwMjUxZWMwZDdjIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSectionc4c9ec86076a26b5930d",
                "icon": "fa-solid fa-file-invoice-dollar",
                "group": "Finance",
            },
            {
                "id": "bluebeam",
                "name": "Bluebeam Development Projects",
                "description": "Bluebeam Summary",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiN2JlOTJmMDQtOThmZC00YWNlLWI3NTMtMWExYTBjNzdlNzIwIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSection",
                "icon": "fas fa-file-alt",
                "group": "Community Development",
            },
            {
                "id": "permits_inspections",
                "name": "Permits and Inspections",
                "description": "Permit and Inspections Trends and Summaries",
                "embed_url": "https://app.powerbi.com/view?r=eyJrIjoiNzI0MmM5ZTYtM2E3NC00MDJlLWE5NWYtODAzMDk0ZmIzYmZlIiwidCI6ImM5OTZiMGQwLWRlZTgtNGM5NC1iMDllLTM0NTc5ODM0OGYxYSIsImMiOjF9&pageName=ReportSectionbe6c43737b1fd78bdffc",
                "icon": "fa-solid fa-file-circle-check",
                "group": "Community Development",
            },
        ]

        # Find the requested report
        report = next((r for r in reports if r["id"] == report_id), None)

        if report:
            logger.info("Rendering Power BI report: %s", report["name"])
            return render_template(
                "groups/powerbi/embed.html",
                title=report["name"],
                report=report,
                reports=reports,  # Pass all reports for navigation
            )
        else:
            logger.error("Power BI report not found: %s", report_id)
            return render_template(
                "error.html", error=f"Report '{report_id}' not found"
            )

    except Exception as e:
        logger.error("Error rendering Power BI report %s: %s", report_id, str(e))
        return render_template("error.html", error=str(e))


@bp.route("/report-status", methods=["POST"])
def report_status():
    """
    API endpoint to log report loading status.

    Returns:
        Response: JSON response.
    """
    try:
        data = request.json
        report_id = data.get("reportId")
        status = data.get("status")
        message = data.get("message", "")

        if status == "success":
            logger.info("Power BI report loaded successfully: %s", report_id)
        else:
            logger.error("Power BI report loading failed: %s - %s", report_id, message)

        return jsonify({"success": True})

    except Exception as e:
        logger.error("Error processing report status: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
