"""
Work Order Counts Routes.

This module defines the routes for the Work Order Counts report blueprint.
"""

import logging
import csv
from datetime import datetime, timedelta
from io import StringIO

from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.work_order_counts import bp
from app.groups.utilities_billing.work_order_counts.queries import (
    get_work_order_counts_by_user,
    get_work_orders_daily_counts,
    get_work_orders_by_type,
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
        # Default to last 30 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        return render_template(
            "groups/utilities_billing/work_order_counts/index.html",
            title="Work Order Counts Report",
            default_start_date=start_date,
            default_end_date=end_date,
        )

    except Exception as e:
        logger.error("Error rendering report index: %s", str(e))
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

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates (last 30 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=30)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_work_order_counts_by_user(start_date, end_date)

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
        logger.error("Error fetching report data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/daily-counts")
def get_daily_counts():
    """
    Get daily counts of work orders.

    Returns:
        Response: JSON response with daily count data.
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
            # Use default dates (last 30 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=30)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_work_orders_daily_counts(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Convert dates to strings for JSON serialization
        for row in results:
            if row.get("CreateDate"):
                row["CreateDate"] = (
                    row["CreateDate"].strftime("%Y-%m-%d")
                    if hasattr(row["CreateDate"], "strftime")
                    else row["CreateDate"]
                )

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching daily counts data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/type-counts")
def get_type_counts():
    """
    Get work order counts by type.

    Returns:
        Response: JSON response with type count data.
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
            # Use default dates (last 30 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=30)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_work_orders_by_type(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching type counts data: %s", str(e))
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

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates (last 30 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=30)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_work_order_counts_by_user(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        # Write header row
        writer.writerow(["Username", "Work Order Count"])

        # Write data rows
        for row in results:
            writer.writerow([row.get("UserName", ""), row.get("CountUser", "")])

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"work_order_counts_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
