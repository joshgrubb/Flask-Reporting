"""
Cycle Info Routes.

This module defines the routes for the Cycle Info report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.cycle_info import bp
from app.groups.utilities_billing.cycle_info.queries import (
    get_cycle_info,
    get_available_cycles,
    get_cycle_summary,
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
        # Get available cycles for the filter dropdown
        query, params, db_key = get_available_cycles()
        cycles = execute_query(query, params, db_key=db_key)

        # Convert to simple list for template
        cycle_list = [cycle["Cycle"] for cycle in cycles]

        return render_template(
            "groups/utilities_billing/cycle_info/index.html",
            title="Cycle Info Report",
            cycles=cycle_list,
        )

    except Exception as e:
        logger.error("Error rendering Cycle Info report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get filter parameters
        cycles_param = request.args.get("cycles", "")

        # Parse cycles if provided
        cycles = None
        if cycles_param:
            cycles = cycles_param.split(",")

        # Get query and parameters
        query, params, db_key = get_cycle_info(cycles)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "cycles": cycles_param,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching cycle info data: %s", str(e))
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
        query, params, db_key = get_cycle_summary()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
            }
        )

    except Exception as e:
        logger.error("Error fetching cycle summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get filter parameters
        cycles_param = request.args.get("cycles", "")

        # Parse cycles if provided
        cycles = None
        if cycles_param:
            cycles = cycles_param.split(",")

        # Get query and parameters
        query, params, db_key = get_cycle_info(cycles)

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
                "Customer Name",
                "Email Address",
                "Full Address",
                "Cycle",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("FullAccountNumber", ""),
                    row.get("FormalName", ""),
                    row.get("EmailAddress", ""),
                    row.get("FullAddress", ""),
                    row.get("Cycle", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cycle_info_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting cycle info report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
