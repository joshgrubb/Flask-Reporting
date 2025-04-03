"""
FIFO Work Order Cost Report Routes.

This module defines the routes for the FIFO Work Order Cost report blueprint.
"""

import logging
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, Response
import csv
from io import StringIO

from app.core.database import execute_query
from app.groups.warehouse.fifo_cost_wo import bp
from app.groups.warehouse.fifo_cost_wo.queries import (
    get_fifo_work_order_costs,
    get_work_order_summary,
    format_date_for_query,
    get_default_date_range,
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
        # Get default date range (last complete calendar month)
        start_date, end_date = get_default_date_range()
        default_start_date = start_date.strftime("%Y-%m-%d")
        default_end_date = end_date.strftime("%Y-%m-%d")

        return render_template(
            "groups/warehouse/fifo_cost_wo/index.html",
            title="FIFO Work Order Cost Report",
            default_start_date=default_start_date,
            default_end_date=default_end_date,
        )

    except Exception as e:
        logger.error("Error rendering FIFO Work Order Cost report index: %s", str(e))
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
        query, params, db_key = get_fifo_work_order_costs(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process the results to group by work order
        work_orders = {}
        for row in results:
            wo_id = row["WORKORDERID"]
            if wo_id not in work_orders:
                work_orders[wo_id] = {
                    "WORKORDERID": wo_id,
                    "WOCATEGORY": row["WOCATEGORY"],
                    "TRANSDATE": row["TRANSDATE"],
                    "ITEMS": [],
                    "TOTAL_COST": 0,
                    "MISSING_ACCT": False,
                }

            # Add the material item
            work_orders[wo_id]["ITEMS"].append(
                {
                    "MATERIALUID": row["MATERIALUID"],
                    "DESCRIPTION": row["DESCRIPTION"],
                    "UNITSREQUIRED": row["UNITSREQUIRED"],
                    "COST": row["COST"],
                    "ACCTNUM": row["ACCTNUM"],
                }
            )

            # Add to total cost
            work_orders[wo_id]["TOTAL_COST"] += float(row["COST"] or 0)

            # Check if this item is missing an account number
            if row["ACCTNUM"] is None or row["ACCTNUM"] == "":
                work_orders[wo_id]["MISSING_ACCT"] = True

        # Convert to list for JSON
        work_order_list = list(work_orders.values())

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": work_order_list,
                "count": len(work_order_list),
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching work order cost data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with summary data.
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
        query, params, db_key = get_work_order_summary(start_date, end_date)

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
        logger.error("Error fetching summary data: %s", str(e))
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
        query, params, db_key = get_fifo_work_order_costs(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        # Write header row
        writer.writerow(results[0].keys())

        # Write data rows
        for row in results:
            writer.writerow(row.values())

        # Create response with CSV file
        output = si.getvalue()
        filename = f"fifo_work_order_costs_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
