"""
Sewer Clean Length Routes.

This module defines the routes for the Sewer Clean Length report blueprint.
"""

import logging
import csv
from datetime import datetime, timedelta
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.water_resources.sewer_clean_length import bp
from app.groups.water_resources.sewer_clean_length.queries import (
    get_sewer_clean_data,
    get_daily_totals,
    get_description_totals,
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
            "groups/water_resources/sewer_clean_length/index.html",
            title="Sewer Clean Length Report",
            default_start_date=start_date,
            default_end_date=end_date,
        )

    except Exception as e:
        logger.error("Error rendering sewer clean length report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_data():
    """
    Get sewer clean data as JSON for AJAX requests.

    Returns:
        Response: JSON response with sewer clean data.
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
        query, params, db_key = get_sewer_clean_data(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process date fields for JSON serialization
        for row in results:
            if row.get("actualfinishdate"):
                row["actualfinishdate"] = (
                    row["actualfinishdate"].isoformat()
                    if hasattr(row["actualfinishdate"], "isoformat")
                    else row["actualfinishdate"]
                )

            # Convert length from meters to feet (if needed)
            if row.get("length"):
                # Assuming the length is in meters and we want to show feet
                # If it's already in feet, remove this conversion
                row["length_ft"] = float(row["length"]) * 3.28084  # meters to feet

        # Also get summary data (daily totals and description totals)
        daily_query, daily_params, daily_db_key = get_daily_totals(start_date, end_date)
        daily_results = execute_query(daily_query, daily_params, db_key=daily_db_key)

        for row in daily_results:
            if row.get("clean_date"):
                row["clean_date"] = (
                    row["clean_date"].isoformat()
                    if hasattr(row["clean_date"], "isoformat")
                    else row["clean_date"]
                )

            # Convert total_length from meters to feet
            if row.get("total_length"):
                row["total_length_ft"] = (
                    float(row["total_length"]) * 3.28084
                )  # meters to feet

        # Get description totals
        desc_query, desc_params, desc_db_key = get_description_totals(
            start_date, end_date
        )
        desc_results = execute_query(desc_query, desc_params, db_key=desc_db_key)

        for row in desc_results:
            # Convert total_length from meters to feet
            if row.get("total_length"):
                row["total_length_ft"] = (
                    float(row["total_length"]) * 3.28084
                )  # meters to feet

        # Calculate overall totals
        total_length = sum(float(row.get("length", 0)) for row in results)
        total_length_ft = total_length * 3.28084  # meters to feet
        total_work_orders = len(set(row.get("workorderid") for row in results))

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "daily_totals": daily_results,
                "description_totals": desc_results,
                "summary": {
                    "total_length": total_length,
                    "total_length_ft": total_length_ft,
                    "total_work_orders": total_work_orders,
                },
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching sewer clean data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_data():
    """
    Export sewer clean data to CSV.

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
        query, params, db_key = get_sewer_clean_data(start_date, end_date)

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
                "Entity UID",
                "Object ID",
                "Length (m)",
                "Length (ft)",
            ]
        )

        # Write data rows
        for row in results:
            # Convert length to feet
            length_m = float(row.get("length", 0))
            length_ft = length_m * 3.28084

            writer.writerow(
                [
                    row.get("workorderid", ""),
                    row.get("description", ""),
                    row.get("actualfinishdate", ""),
                    row.get("entityuid", ""),
                    row.get("objectid", ""),
                    f"{length_m:.2f}",
                    f"{length_ft:.2f}",
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sewer_clean_data_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting sewer clean data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary-export")
def export_summary():
    """
    Export sewer clean summary data to CSV.

    Returns:
        Response: CSV file download with daily and type totals.
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

        # Get daily summary data
        daily_query, daily_params, daily_db_key = get_daily_totals(start_date, end_date)
        daily_results = execute_query(daily_query, daily_params, db_key=daily_db_key)

        # Get description summary data
        desc_query, desc_params, desc_db_key = get_description_totals(
            start_date, end_date
        )
        desc_results = execute_query(desc_query, desc_params, db_key=desc_db_key)

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        # Write first header for daily data
        writer.writerow(["Daily Cleaning Totals"])
        writer.writerow(
            ["Date", "Work Order Count", "Total Length (m)", "Total Length (ft)"]
        )

        # Write daily data
        for row in daily_results:
            length_m = float(row.get("total_length", 0))
            length_ft = length_m * 3.28084

            writer.writerow(
                [
                    row.get("clean_date", ""),
                    row.get("work_order_count", ""),
                    f"{length_m:.2f}",
                    f"{length_ft:.2f}",
                ]
            )

        # Add separator
        writer.writerow([])
        writer.writerow([])

        # Write second header for work type data
        writer.writerow(["Work Type Cleaning Totals"])
        writer.writerow(
            ["Work Type", "Work Order Count", "Total Length (m)", "Total Length (ft)"]
        )

        # Write work type data
        for row in desc_results:
            length_m = float(row.get("total_length", 0))
            length_ft = length_m * 3.28084

            writer.writerow(
                [
                    row.get("work_type", ""),
                    row.get("work_order_count", ""),
                    f"{length_m:.2f}",
                    f"{length_ft:.2f}",
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sewer_clean_summary_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting sewer clean summary: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
