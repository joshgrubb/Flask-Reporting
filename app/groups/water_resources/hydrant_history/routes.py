# app/groups/water_resources/hydrant_history/routes.py
"""
Hydrant History Routes.

This module defines the routes for the Hydrant History report blueprint.
"""

import logging
import csv
from datetime import datetime, timedelta
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.water_resources.hydrant_history import bp
from app.groups.water_resources.hydrant_history.queries import (
    get_hydrant_inspections,
    get_hydrant_work_orders,
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
            "groups/water_resources/hydrant_history/index.html",
            title="Hydrant History Report",
            default_start_date=start_date,
            default_end_date=end_date,
        )

    except Exception as e:
        logger.error("Error rendering hydrant history report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/inspections")
def get_inspections_data():
    """
    Get hydrant inspection data as JSON for AJAX requests.

    Returns:
        Response: JSON response with inspection data.
    """
    try:
        # Get date filters and hydrant ID from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        hydrant_id = request.args.get("hydrant_id", "")

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
        query, params, db_key = get_hydrant_inspections(
            start_date, end_date, hydrant_id if hydrant_id else None
        )

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process date fields for JSON serialization
        for row in results:
            if row.get("INSPDATE"):
                row["INSPDATE"] = (
                    row["INSPDATE"].isoformat()
                    if hasattr(row["INSPDATE"], "isoformat")
                    else row["INSPDATE"]
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
                    "hydrant_id": hydrant_id,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching hydrant inspection data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/work-orders")
def get_work_orders_data():
    """
    Get hydrant work order data as JSON for AJAX requests.

    Returns:
        Response: JSON response with work order data.
    """
    try:
        # Get date filters and hydrant ID from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        hydrant_id = request.args.get("hydrant_id", "")

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
        query, params, db_key = get_hydrant_work_orders(
            start_date, end_date, hydrant_id if hydrant_id else None
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
                    "hydrant_id": hydrant_id,
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching hydrant work order data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export-inspections")
def export_inspections():
    """
    Export hydrant inspection data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get date filters and hydrant ID from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        hydrant_id = request.args.get("hydrant_id", "")

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
        query, params, db_key = get_hydrant_inspections(
            start_date, end_date, hydrant_id if hydrant_id else None
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
                "Inspection ID",
                "Work Order ID",
                "Template Name",
                "Hydrant ID",
                "Entity Type",
                "Inspection Date",
                "Status",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("INSPECTIONID", ""),
                    row.get("WORKORDERID", ""),
                    row.get("INSPTEMPLATENAME", ""),
                    row.get("ENTITYUID", ""),
                    row.get("ENTITYTYPE", ""),
                    row.get("INSPDATE", ""),
                    row.get("STATUS", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hydrant_inspections_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting hydrant inspections: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export-work-orders")
def export_work_orders():
    """
    Export hydrant work order data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get date filters and hydrant ID from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        hydrant_id = request.args.get("hydrant_id", "")

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
        query, params, db_key = get_hydrant_work_orders(
            start_date, end_date, hydrant_id if hydrant_id else None
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
                "Description",
                "Finish Date",
                "Status",
                "Hydrant ID",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("WORKORDERID", ""),
                    row.get("DESCRIPTION", ""),
                    row.get("ACTUALFINISHDATE", ""),
                    row.get("STATUS", ""),
                    row.get("ENTITYUID", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hydrant_work_orders_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting hydrant work orders: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
