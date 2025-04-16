# app/groups/public_works/fleet_costs/routes.py
"""
Fleet Costs Routes.

This module defines the routes for the Fleet Costs report blueprint.
"""

import logging
import csv
from datetime import datetime, timedelta, timezone
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.public_works.fleet_costs import bp
from app.groups.public_works.fleet_costs.queries import (
    get_fleet_costs,
    get_departments,
    get_cost_summary_by_department,
    get_cost_summary_by_vehicle,
    format_date_for_query,
    get_costs_over_time,
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
        # Default to last 90 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        # Get list of departments
        query, params, db_key = get_departments()
        departments = execute_query(query, params, db_key=db_key)

        # Convert to simpler format for dropdown
        department_list = [dept["Department"] for dept in departments]

        return render_template(
            "groups/public_works/fleet_costs/index.html",
            title="Fleet Costs Report",
            default_start_date=start_date,
            default_end_date=end_date,
            departments=department_list,
        )

    except Exception as e:
        logger.error("Error rendering fleet costs report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get date filters and department from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        department = request.args.get("department", "")

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            )
        else:
            # Use default dates (last 90 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (start_date - timedelta(days=90)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_fleet_costs(
            start_date, end_date, department if department else None
        )

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process date fields for JSON serialization
        for row in results:
            if row.get("ACTUALFINISHDATE"):
                row["ACTUALFINISHDATE"] = (
                    row["ACTUALFINISHDATE"].isoformat()
                    if hasattr(row["ACTUALFINISHDATE"], "isoformat")
                    else row["ACTUALFINISHDATE"]
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
                    "department": department,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching fleet costs data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary/department")
def get_department_summary():
    """
    Get cost summary by department as JSON for AJAX requests.

    Returns:
        Response: JSON response with department summary data.
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
            # Use default dates (last 90 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=90)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_cost_summary_by_department(start_date, end_date)

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
        logger.error("Error fetching department summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary/vehicle")
def get_vehicle_summary():
    """
    Get cost summary by vehicle as JSON for AJAX requests.

    Returns:
        Response: JSON response with vehicle summary data.
    """
    try:
        # Get date filters and department from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        department = request.args.get("department", "")

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates (last 90 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=90)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_cost_summary_by_vehicle(
            start_date, end_date, department if department else None
        )

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
                    "department": department,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching vehicle summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export fleet costs data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get date filters and department from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        department = request.args.get("department", "")

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates (last 90 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=90)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_fleet_costs(
            start_date, end_date, department if department else None
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
                "Work Order ID",
                "Finish Date",
                "Category",
                "Labor Cost",
                "Material Cost",
                "Total Cost",
                "Account Number",
                "Status",
                "Work Order SID",
                "Vehicle ID",
                "Vehicle Model",
                "Department",
            ]
        )

        # Write data rows
        for row in results:
            # Calculate total cost
            labor_cost = row.get("WOLABORCOST", 0) or 0
            material_cost = row.get("WOMATCOST", 0) or 0
            total_cost = labor_cost + material_cost

            writer.writerow(
                [
                    row.get("WORKORDERID", ""),
                    row.get("ACTUALFINISHDATE", ""),
                    row.get("WOCATEGORY", ""),
                    labor_cost,
                    material_cost,
                    total_cost,
                    row.get("ACCTNUM", ""),
                    row.get("STATUS", ""),
                    row.get("WORKORDERSID", ""),
                    row.get("ENTITYUID", ""),
                    row.get("Model", ""),
                    row.get("Department", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fleet_costs_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting fleet costs data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/time-series")
def get_time_series_data():
    """
    Get costs over time data as JSON for AJAX requests.

    Returns:
        Response: JSON response with time series data.
    """
    try:
        # Get date filters, department, and interval from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        department = request.args.get("department", "")
        interval = request.args.get("interval", "month")

        # Validate interval
        valid_intervals = ["day", "week", "month", "quarter", "year"]
        if interval not in valid_intervals:
            interval = "month"  # Default to month if invalid

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            # Fix: Make sure end date is the end of the day to include all data
            end_date = end_date.replace(hour=23, minute=59, second=59)

            # Debug logging
            logger.info(
                "Time series request with interval %s from %s to %s",
                interval,
                start_date.strftime("%Y-%m-%d %H:%M:%S"),
                end_date.strftime("%Y-%m-%d %H:%M:%S"),
            )
        else:
            # Use default dates (last 90 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=90)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_costs_over_time(
            start_date, end_date, department if department else None, interval
        )

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Add debug logging for the data
        logger.debug("Time series query results count: %d", len(results))
        if interval == "year":
            years = [
                (
                    result["TimePeriod"].year
                    if hasattr(result["TimePeriod"], "year")
                    else "unknown"
                )
                for result in results
            ]
            logger.debug("Years in results: %s", years)

        # Process date fields for JSON serialization
        for row in results:
            if row.get("TimePeriod"):
                row["TimePeriod"] = (
                    row["TimePeriod"].strftime("%Y-%m-%d")
                    if hasattr(row["TimePeriod"], "strftime")
                    else row["TimePeriod"]
                )

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "department": department,
                    "interval": interval,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching time series data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
