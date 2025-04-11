"""
Credit Balance Routes.

This module defines the routes for the Credit Balance report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.credit_balance import bp
from app.groups.utilities_billing.credit_balance.queries import (
    get_credit_balance_accounts,
    get_credit_balance_summary,
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
            "groups/utilities_billing/credit_balance/index.html",
            title="Credit Balance Report",
        )

    except Exception as e:
        logger.error("Error rendering Credit Balance report index: %s", str(e))
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
        query, params, db_key = get_credit_balance_accounts()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format dates for JSON serialization
        for row in results:
            if row.get("MoveOutDate"):
                row["MoveOutDate"] = (
                    row["MoveOutDate"].isoformat()
                    if hasattr(row["MoveOutDate"], "isoformat")
                    else row["MoveOutDate"]
                )

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
            }
        )

    except Exception as e:
        logger.error("Error fetching credit balance data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary statistics as JSON for AJAX requests.

    Returns:
        Response: JSON response with summary statistics.
    """
    try:
        # Get query and parameters for summary
        query, params, db_key = get_credit_balance_summary()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format monetary values for display
        if results and len(results) > 0:
            summary = results[0]
        else:
            summary = {
                "TotalAccounts": 0,
                "TotalCreditAmount": 0,
                "AvgCreditAmount": 0,
                "MinCreditAmount": 0,
                "MaxCreditAmount": 0,
            }

        # Return data as JSON
        return jsonify({"success": True, "data": summary})

    except Exception as e:
        logger.error("Error fetching credit balance summary: %s", str(e))
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
        query, params, db_key = get_credit_balance_accounts()

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
                "Balance",
                "Customer Name",
                "Address",
                "Email Address",
                "Move Out Date",
                "Cell Phone",
                "Primary Phone",
                "Account Status",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("FullAccountNumber", ""),
                    row.get("LastBalance", ""),
                    row.get("FormalName", ""),
                    row.get("FullAddress", ""),
                    row.get("EmailAddress", ""),
                    row.get("MoveOutDate", ""),
                    row.get("CellPhone", ""),
                    row.get("PrimaryPhone", ""),
                    row.get("AccountStatus", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        filename = f"credit_balance_report_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting credit balance report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
