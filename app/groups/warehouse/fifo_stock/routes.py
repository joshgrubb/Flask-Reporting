"""
FIFO Stock Cost Routes.

This module defines the routes for the FIFO Stock Cost report blueprint.
"""

import logging
from datetime import datetime
from flask import render_template, request, jsonify, Response
import csv
from io import StringIO

from app.core.database import execute_query
from app.groups.warehouse.fifo_stock import bp
from app.groups.warehouse.fifo_stock.queries import (
    get_inventory_by_category,
    get_inventory_categories,
    get_inventory_summary_by_category,
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
            "groups/warehouse/fifo_stock/index.html",
            title="Inventory By Category Report",
        )

    except Exception as e:
        logger.error("Error rendering FIFO Stock Cost report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/categories")
def get_categories():
    """
    Get list of available inventory categories.

    Returns:
        Response: JSON response with categories data.
    """
    try:
        # Get query and parameters
        query, params, db_key = get_inventory_categories()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Convert to simple list for the dropdown
        categories = [row["CATEGORY"] for row in results]

        # Return data as JSON
        return jsonify({"success": True, "data": categories})

    except Exception as e:
        logger.error("Error fetching inventory categories: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get category filter from request
        category = request.args.get("category", "")

        if not category:
            return jsonify({"success": False, "error": "Please select a category"}), 400

        # Get query and parameters
        query, params, db_key = get_inventory_by_category(category)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "category": category,
            }
        )

    except Exception as e:
        logger.error("Error fetching inventory data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/summary")
def get_summary_data():
    """
    Get summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with summary data.
    """
    try:
        # Get category filter from request
        category = request.args.get("category", "")

        if not category:
            return jsonify({"success": False, "error": "Please select a category"}), 400

        # Get query and parameters
        query, params, db_key = get_inventory_summary_by_category(category)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process total value for the entire category
        total_category_value = sum(float(item["TotalValue"] or 0) for item in results)
        total_category_quantity = sum(
            int(item["TotalQuantity"] or 0) for item in results
        )

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "category": category,
                "totalValue": total_category_value,
                "totalQuantity": total_category_quantity,
            }
        )

    except Exception as e:
        logger.error("Error fetching inventory summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get category filter and export type from request
        category = request.args.get("category", "")
        export_type = request.args.get("type", "detail")  # 'detail' or 'summary'

        if not category:
            return jsonify({"success": False, "error": "Please select a category"}), 400

        # Get query and parameters based on export type
        if export_type == "summary":
            query, params, db_key = get_inventory_summary_by_category(category)
        else:
            query, params, db_key = get_inventory_by_category(category)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No data found for the selected category",
                    }
                ),
                404,
            )

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
        filename = f"inventory_{category}_{export_type}_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
