"""
Cut for Nonpayment Routes.

This module defines the routes for the Cut for Nonpayment report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.cut_nonpayment import bp
from app.groups.utilities_billing.cut_nonpayment.queries import (
    get_cut_nonpayment_accounts,
    get_available_cycles,
    get_cut_nonpayment_summary,
    format_date_for_query,
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
            "groups/utilities_billing/cut_nonpayment/index.html",
            title="Cut for Nonpayment Report",
            cycles=cycle_list,
        )

    except Exception as e:
        logger.error("Error rendering Cut for Nonpayment report index: %s", str(e))
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
        cut_date_str = request.args.get("cut_date", "")
        cycles_param = request.args.get("cycles", "")

        # Parse cut date if provided
        cut_date = None
        if cut_date_str:
            cut_date = datetime.strptime(cut_date_str, "%Y-%m-%d")
            # Set to beginning of day
            cut_date = cut_date.replace(hour=0, minute=0, second=0)

        # Parse cycles if provided
        cycles = None
        if cycles_param:
            cycles = cycles_param.split(",")

        # Get query and parameters
        query, params, db_key = get_cut_nonpayment_accounts(cut_date, cycles)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "cut_date": cut_date_str,
                    "cycles": cycles_param,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching cut for nonpayment data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with summary data.
    """
    try:
        # Get filter parameters
        cut_date_str = request.args.get("cut_date", "")
        cycles_param = request.args.get("cycles", "")

        # Parse cut date if provided
        cut_date = None
        if cut_date_str:
            cut_date = datetime.strptime(cut_date_str, "%Y-%m-%d")
            # Set to beginning of day
            cut_date = cut_date.replace(hour=0, minute=0, second=0)

        # Parse cycles if provided
        cycles = None
        if cycles_param:
            cycles = cycles_param.split(",")

        # Get query and parameters
        query, params, db_key = get_cut_nonpayment_summary(cut_date, cycles)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "cut_date": cut_date_str,
                    "cycles": cycles_param,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching cut for nonpayment summary: %s", str(e))
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
        cut_date_str = request.args.get("cut_date", "")
        cycles_param = request.args.get("cycles", "")

        # Parse cut date if provided
        cut_date = None
        if cut_date_str:
            cut_date = datetime.strptime(cut_date_str, "%Y-%m-%d")
            # Set to beginning of day
            cut_date = cut_date.replace(hour=0, minute=0, second=0)

        # Parse cycles if provided
        cycles = None
        if cycles_param:
            cycles = cycles_param.split(",")

        # Get query and parameters
        query, params, db_key = get_cut_nonpayment_accounts(cut_date, cycles)

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
                "Last Name",
                "First Name",
                "Address",
                "Cycle",
                "Account Type",
                "Number of Cuts",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("FullAccountNumber", ""),
                    row.get("LastName", ""),
                    row.get("FirstName", ""),
                    row.get("FullAddress", ""),
                    row.get("Cycle", ""),
                    row.get("AccountType", ""),
                    row.get("CUTS", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cut_for_nonpayment_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting cut for nonpayment report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
