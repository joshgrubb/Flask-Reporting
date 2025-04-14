"""
High Balance Routes.

This module defines the routes for the High Balance report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from typing import List, Dict, Any

from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.high_balance import bp
from app.groups.utilities_billing.high_balance.queries import (
    get_high_balance_accounts,
    get_account_type_options,
    get_high_balance_summary,
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
        # Get account type options for the filter dropdown
        query, params, db_key = get_account_type_options()
        account_types = execute_query(query, params, db_key=db_key)

        return render_template(
            "groups/utilities_billing/high_balance/index.html",
            title="High Balance Report",
            account_types=account_types,
            default_balance=1000.00,  # Default threshold of $1000
        )

    except Exception as e:
        logger.error("Error rendering High Balance report index: %s", str(e))
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
        try:
            balance_threshold = float(request.args.get("balance", "1000.00"))
        except ValueError:
            balance_threshold = 1000.00  # Default if invalid

        # Get account types parameter
        account_types_param = request.args.get("account_types", "")

        # Parse account types if provided
        account_types = (
            account_types_param.split(",") if account_types_param else ["477"]
        )  # Default to residential

        # Get query and parameters
        query, params, db_key = get_high_balance_accounts(
            balance_threshold, account_types
        )

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format monetary values for display
        for row in results:
            if "Balance" in row:
                row["Balance"] = float(row["Balance"])

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "balance": balance_threshold,
                    "account_types": account_types,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching high balance data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary data for high balance accounts.

    Returns:
        Response: JSON response with summary data.
    """
    try:
        # Get filter parameters
        try:
            balance_threshold = float(request.args.get("balance", "1000.00"))
        except ValueError:
            balance_threshold = 1000.00  # Default if invalid

        # Get account types parameter
        account_types_param = request.args.get("account_types", "")

        # Parse account types if provided
        account_types = (
            account_types_param.split(",") if account_types_param else ["477"]
        )  # Default to residential

        # Get query and parameters
        query, params, db_key = get_high_balance_summary(
            balance_threshold, account_types
        )

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format monetary values for display
        for row in results:
            for key in ["TotalBalance", "AverageBalance", "MaxBalance", "MinBalance"]:
                if key in row:
                    row[key] = float(row[key])

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
            }
        )

    except Exception as e:
        logger.error("Error fetching high balance summary: %s", str(e))
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
        try:
            balance_threshold = float(request.args.get("balance", "1000.00"))
        except ValueError:
            balance_threshold = 1000.00  # Default if invalid

        # Get account types parameter
        account_types_param = request.args.get("account_types", "")

        # Parse account types if provided
        account_types = (
            account_types_param.split(",") if account_types_param else ["477"]
        )  # Default to residential

        # Get query and parameters
        query, params, db_key = get_high_balance_accounts(
            balance_threshold, account_types
        )

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
                "Account Type",
                "Address",
                "Last Name",
                "First Name",
                "Email",
                "Phone",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("FullAccountNumber", ""),
                    "${:.2f}".format(float(row.get("Balance", 0))),
                    row.get("AccountType", ""),
                    row.get("FullAddress", ""),
                    row.get("LastName", ""),
                    row.get("FirstName", ""),
                    row.get("EmailAddress", ""),
                    row.get("PrimaryPhone", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"high_balance_report_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting high balance report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
