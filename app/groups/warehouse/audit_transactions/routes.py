"""
Warehouse Audit Transactions Routes.

This module defines the routes for the Warehouse Audit Transactions report blueprint.
"""

import logging
import csv
from datetime import datetime, timedelta
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.warehouse.audit_transactions import bp
from app.groups.warehouse.audit_transactions.queries import (
    get_audit_transactions,
    get_account_summary,
    get_material_summary,
    get_default_date_range,
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
        # Get default date range (previous month)
        start_date, end_date = get_default_date_range()
        default_start_date = start_date.strftime("%Y-%m-%d")
        default_end_date = end_date.strftime("%Y-%m-%d")

        return render_template(
            "groups/warehouse/audit_transactions/index.html",
            title="Warehouse Audit Transactions",
            default_start_date=default_start_date,
            default_end_date=default_end_date,
        )

    except Exception as e:
        logger.error("Error rendering audit transactions report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get date filters from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        account_number = request.args.get("account_number", "")
        material_id = request.args.get("material_id", "")

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates (previous month)
            start_date, end_date = get_default_date_range()

        # Build filters dictionary for query parameters
        filters = {
            "account_number": account_number or None,
            "material_id": material_id or None,
        }

        # Get query and parameters
        query, params, db_key = get_audit_transactions(
            start_date, end_date, filters["account_number"], filters["material_id"]
        )

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process datetime fields for JSON serialization
        for row in results:
            if row.get("TRANSDATETIME"):
                row["TRANSDATETIME"] = (
                    row["TRANSDATETIME"].isoformat()
                    if hasattr(row["TRANSDATETIME"], "isoformat")
                    else row["TRANSDATETIME"]
                )

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "account_number": filters["account_number"],
                    "material_id": filters["material_id"],
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching audit transactions data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/account-summary")
def get_accounts_summary():
    """
    Get account summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with account summary data.
    """
    try:
        # Get date filters from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates
            start_date, end_date = get_default_date_range()

        # Get query and parameters
        query, params, db_key = get_account_summary(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching account summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/material-summary")
def get_materials_summary():
    """
    Get material summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with material summary data.
    """
    try:
        # Get date filters from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates
            start_date, end_date = get_default_date_range()

        # Get query and parameters
        query, params, db_key = get_material_summary(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching material summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get date filters from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        account_number = request.args.get("account_number", "")
        material_id = request.args.get("material_id", "")

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates
            start_date, end_date = get_default_date_range()

        # Get query and parameters with filters
        query, params, db_key = get_audit_transactions(
            start_date, end_date, account_number or None, material_id or None
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
                "Transaction ID",
                "Transaction Date/Time",
                "Transaction Type",
                "Personnel",
                "Issue Work Order ID",
                "Receive Work Order ID",
                "Material ID",
                "Description",
                "Old Quantity",
                "New Quantity",
                "Old Unit Cost",
                "New Unit Cost",
                "GL Account",
                "Cost Difference",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("TRANSACTIONID", ""),
                    row.get("TRANSDATETIME", ""),
                    row.get("TRANSTYPE", ""),
                    row.get("PERSONNEL", ""),
                    row.get("ISSUE_WORKORDERID", ""),
                    row.get("RECEIVE_WORKORDERID", ""),
                    row.get("MATERIALUID", ""),
                    row.get("DESCRIPTION", ""),
                    row.get("OLDQUANT", ""),
                    row.get("NEWQUANT", ""),
                    row.get("OLDUNITCOST", ""),
                    row.get("NEWUNITCOST", ""),
                    row.get("ACCTNUM", ""),
                    row.get("COSTDIFF", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"warehouse_audit_transactions_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting audit transactions report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
