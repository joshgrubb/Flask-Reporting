"""
Cash Only Accounts Routes.

This module defines the routes for the Cash Only Accounts report blueprint.
"""

import logging
from datetime import datetime
from flask import render_template, request, jsonify, Response
import csv
from io import StringIO

from app.core.database import execute_query
from app.groups.utilities_billing.cash_only_accounts import bp
from app.groups.utilities_billing.cash_only_accounts.queries import (
    get_cash_only_accounts,
    get_cash_only_accounts_summary,
    get_accounts_by_date_range,
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
            "groups/utilities_billing/cash_only_accounts/index.html",
            title="Cash Only Accounts Report",
        )

    except Exception as e:
        logger.error("Error rendering Cash Only Accounts report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get date range parameters if provided
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        # Parse dates if provided
        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            # Set to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Get query and parameters based on date filtering
        if start_date or end_date:
            query, params, db_key = get_accounts_by_date_range(start_date, end_date)
        else:
            query, params, db_key = get_cash_only_accounts()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format dates for JSON serialization
        for row in results:
            if row.get("MessageStartDate"):
                row["MessageStartDate"] = (
                    row["MessageStartDate"].isoformat()
                    if isinstance(row["MessageStartDate"], datetime)
                    else row["MessageStartDate"]
                )
            if row.get("MessageEndDate"):
                row["MessageEndDate"] = (
                    row["MessageEndDate"].isoformat()
                    if isinstance(row["MessageEndDate"], datetime)
                    else row["MessageEndDate"]
                )

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching cash only accounts data: %s", str(e))
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
        query, params, db_key = get_cash_only_accounts_summary()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format dates for JSON serialization
        if results and len(results) > 0:
            summary = results[0]
            if summary.get("OldestMessageDate"):
                summary["OldestMessageDate"] = (
                    summary["OldestMessageDate"].isoformat()
                    if isinstance(summary["OldestMessageDate"], datetime)
                    else summary["OldestMessageDate"]
                )
            if summary.get("NewestMessageDate"):
                summary["NewestMessageDate"] = (
                    summary["NewestMessageDate"].isoformat()
                    if isinstance(summary["NewestMessageDate"], datetime)
                    else summary["NewestMessageDate"]
                )
        else:
            summary = {
                "TotalAccounts": 0,
                "OldestMessageDate": None,
                "NewestMessageDate": None,
                "NoEndDateCount": 0,
                "DaysSinceOldest": 0,
            }

        # Return data as JSON
        return jsonify({"success": True, "data": summary})

    except Exception as e:
        logger.error("Error fetching cash only accounts summary: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get date range parameters if provided
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        # Parse dates if provided
        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            # Set to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Get query and parameters based on date filtering
        if start_date or end_date:
            query, params, db_key = get_accounts_by_date_range(start_date, end_date)
        else:
            query, params, db_key = get_cash_only_accounts()

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
                "Utility Account ID",
                "Account Number",
                "Message Start Date",
                "Message End Date",
                "Internal Message ID",
                "Message",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row["UtilityAccountID"],
                    row["FullAccountNumber"],
                    row["MessageStartDate"],
                    row["MessageEndDate"] if row["MessageEndDate"] else "No End Date",
                    row["InternalMessageID"],
                    row["Message"],
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        filename = f"cash_only_accounts_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting cash only accounts report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
