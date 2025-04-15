# app/groups/warehouse/stock_by_storeroom/routes.py
"""
Stock By Storeroom Routes.

This module defines the routes for the Stock By Storeroom report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.warehouse.stock_by_storeroom import bp
from app.groups.warehouse.stock_by_storeroom.queries import (
    get_storerooms,
    get_stock_by_storeroom,
    get_summary_by_storeroom,
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
        # Get list of storerooms for filter dropdown
        query, params, db_key = get_storerooms()
        storeroom_results = execute_query(query, params, db_key=db_key)

        # Extract storeroom values from results
        storerooms = [room.get("STORERM") for room in storeroom_results]

        # Use the first storeroom as default if available
        default_storeroom = storerooms[0] if storerooms else ""

        return render_template(
            "groups/warehouse/stock_by_storeroom/index.html",
            title="Stock By Storeroom",
            storerooms=storerooms,
            default_storeroom=default_storeroom,
        )

    except Exception as e:
        logger.error("Error rendering Stock By Storeroom report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get storeroom filter from request
        storeroom = request.args.get("storeroom", "")

        if not storeroom:
            return jsonify({"success": False, "error": "No storeroom selected"}), 400

        # Get query and parameters
        query, params, db_key = get_stock_by_storeroom(storeroom)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify({"success": True, "data": results, "count": len(results)})

    except Exception as e:
        logger.error("Error fetching stock by storeroom data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with summary data.
    """
    try:
        # Get storeroom filter from request
        storeroom = request.args.get("storeroom", "")

        if not storeroom:
            return jsonify({"success": False, "error": "No storeroom selected"}), 400

        # Get query and parameters
        query, params, db_key = get_summary_by_storeroom(storeroom)

        # Execute query
        results = execute_query(query, params, db_key=db_key, fetch_all=False)

        # Return data as JSON
        return jsonify({"success": True, "data": results})

    except Exception as e:
        logger.error("Error fetching storeroom summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get storeroom filter from request
        storeroom = request.args.get("storeroom", "")

        if not storeroom:
            return jsonify({"success": False, "error": "No storeroom selected"}), 400

        # Get query and parameters
        query, params, db_key = get_stock_by_storeroom(storeroom)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        # Write header row - custom column names for clarity
        writer.writerow(
            [
                "Material ID",
                "Description",
                "Storeroom",
                "Min Quantity",
                "Stock On Hand",
                "Max Quantity",
                "Under Min",
            ]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("MATERIALUID", ""),
                    row.get("DESCRIPTION", ""),
                    row.get("STORERM", ""),
                    row.get("MINQUANTITY", ""),
                    row.get("STOCKONHAND", ""),
                    row.get("MAXQUANTITY", ""),
                    row.get("Under_Min", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        filename = (
            f"stock_by_storeroom_{storeroom}_{datetime.now().strftime('%Y%m%d')}.csv"
        )

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting stock by storeroom report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
