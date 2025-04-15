"""
Water No Sewer Routes.

This module defines the routes for the Water No Sewer report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.water_no_sewer import bp
from app.groups.utilities_billing.water_no_sewer.queries import (
    get_water_no_sewer_accounts,
    get_account_type_summary,
)

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the main report page.

    Returns:
        str: Rendered HTML template.
    """
    try:
        return render_template(
            "groups/utilities_billing/water_no_sewer/index.html",
            title="Water No Sewer Report",
        )

    except Exception as e:
        logger.error("Error rendering Water No Sewer report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get query and parameters
        query, params, db_key = get_water_no_sewer_accounts()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify({"success": True, "data": results, "count": len(results)})

    except Exception as e:
        logger.error("Error fetching water no sewer data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with summary data.
    """
    try:
        # Get query and parameters
        query, params, db_key = get_account_type_summary()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify({"success": True, "data": results, "count": len(results)})

    except Exception as e:
        logger.error("Error fetching account type summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get query and parameters
        query, params, db_key = get_water_no_sewer_accounts()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        # Write header row
        writer.writerow(
            [
                "Account Number",
                "Account Type",
                "Last Name",
                "First Name",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("FullAccountNumber", ""),
                    row.get("AccountType", ""),
                    row.get("LastName", ""),
                    row.get("FirstName", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        filename = f"water_no_sewer_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting water no sewer report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
