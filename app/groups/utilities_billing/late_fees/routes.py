"""
Late Fees Routes.

This module defines the routes for the Late Fees report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.late_fees import bp
from app.groups.utilities_billing.late_fees.queries import (
    get_late_fees_accounts,
    get_billing_profiles,
    get_late_fees_summary,
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
        # Get billing profiles for the dropdown
        query, params, db_key = get_billing_profiles()
        billing_profiles = execute_query(query, params, db_key=db_key)

        return render_template(
            "groups/utilities_billing/late_fees/index.html",
            title="Late Fees Report",
            billing_profiles=billing_profiles,
        )

    except Exception as e:
        logger.error("Error rendering Late Fees report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get billing profile ID from request
        billing_profile_id = request.args.get("billing_profile", "")

        if not billing_profile_id:
            return (
                jsonify({"success": False, "error": "No billing profile selected"}),
                400,
            )

        # Get query and parameters
        query, params, db_key = get_late_fees_accounts(billing_profile_id)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format dates and monetary values for display
        for row in results:
            if "CurrentDueDate" in row and row["CurrentDueDate"]:
                row["CurrentDueDate"] = (
                    row["CurrentDueDate"].isoformat()
                    if hasattr(row["CurrentDueDate"], "isoformat")
                    else row["CurrentDueDate"]
                )

            # Convert phone numbers to string format with proper formatting
            for phone_field in ["CellPhone", "PrimaryPhone", "WorkPhone"]:
                if phone_field in row and row[phone_field]:
                    try:
                        phone_val = str(row[phone_field])
                        if len(phone_val) == 10:
                            # Format as (XXX) XXX-XXXX
                            row[phone_field] = (
                                f"({phone_val[0:3]}) {phone_val[3:6]}-{phone_val[6:10]}"
                            )
                    except (ValueError, TypeError):
                        # Keep as is if conversion fails
                        pass

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "billing_profile": billing_profile_id,
            }
        )

    except Exception as e:
        logger.error("Error fetching late fees data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary statistics for late fees accounts.

    Returns:
        Response: JSON response with summary data.
    """
    try:
        # Get billing profile ID from request
        billing_profile_id = request.args.get("billing_profile", "")

        if not billing_profile_id:
            return (
                jsonify({"success": False, "error": "No billing profile selected"}),
                400,
            )

        # Get query and parameters
        query, params, db_key = get_late_fees_summary(billing_profile_id)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results[0] if results else {},  # Get first row if exists
                "billing_profile": billing_profile_id,
            }
        )

    except Exception as e:
        logger.error("Error fetching late fees summary: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get billing profile ID from request
        billing_profile_id = request.args.get("billing_profile", "")

        if not billing_profile_id:
            return (
                jsonify({"success": False, "error": "No billing profile selected"}),
                400,
            )

        # Get query and parameters
        query, params, db_key = get_late_fees_accounts(billing_profile_id)

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
                "Due Date",
                "Customer Name",
                "Email Address",
                "Cell Phone",
                "Primary Phone",
                "Work Phone",
                "Exempt Status",
                "Account Status",
            ]
        )

        # Write data rows
        for row in results:
            # Format phone numbers for export
            cell_phone = row.get("CellPhone", "")
            primary_phone = row.get("PrimaryPhone", "")
            work_phone = row.get("WorkPhone", "")

            writer.writerow(
                [
                    row.get("FullAccountNumber", ""),
                    row.get("Balance", ""),
                    row.get("CurrentDueDate", ""),
                    row.get("FormalName", ""),
                    row.get("EmailAddress", ""),
                    cell_phone,
                    primary_phone,
                    work_phone,
                    row.get("Exempt from Penalty", ""),
                    row.get("AccountStatus", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"late_fees_report_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting late fees report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
