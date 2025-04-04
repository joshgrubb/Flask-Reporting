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
    get_inventory_cost_trends,
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
            title="Inventory Cost Trends Report",
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
        # Get category filter and threshold from request
        category = request.args.get("category", "")
        threshold_str = request.args.get("threshold", "50")

        # Parse threshold, with default of 50 if invalid
        try:
            threshold = int(threshold_str)
            if threshold < 1:
                threshold = 50
        except ValueError:
            threshold = 50

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


@bp.route("/cost-trends")
def get_cost_trends_data():
    """
    Get cost trend data as JSON for AJAX requests.

    Returns:
        Response: JSON response with cost trend data.
    """
    try:
        # Get category filter and threshold from request
        category = request.args.get("category", "")
        threshold_str = request.args.get("threshold", "50")

        # Parse threshold, with default of 50 if invalid
        try:
            significant_threshold = int(threshold_str)
            if significant_threshold < 1:
                significant_threshold = 50
        except ValueError:
            significant_threshold = 50

        if not category:
            return jsonify({"success": False, "error": "Please select a category"}), 400

        # Get query and parameters
        query, params, db_key = get_inventory_cost_trends(category)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process data to calculate significant cost increases (potential input errors)
        # using user-defined threshold

        # Group by material to detect patterns
        material_data = {}
        for row in results:
            material_id = row["MATERIALUID"]
            if material_id not in material_data:
                material_data[material_id] = []

            # Determine if this is a significant increase
            if row["PercentChange"] > significant_threshold:
                row["IsSignificantIncrease"] = True
            else:
                row["IsSignificantIncrease"] = False

            material_data[material_id].append(row)

        # Return data as JSON with both grouped and raw results
        return jsonify(
            {
                "success": True,
                "data": results,
                "materialData": material_data,
                "count": len(results),
                "category": category,
                "significantThreshold": significant_threshold,
            }
        )

    except Exception as e:
        logger.error("Error fetching cost trend data: %s", str(e))
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
        export_type = request.args.get(
            "type", "detail"
        )  # 'detail', 'summary' or 'trends'

        if not category:
            return jsonify({"success": False, "error": "Please select a category"}), 400

        # Get query and parameters based on export type
        if export_type == "summary":
            query, params, db_key = get_inventory_summary_by_category(category)
        elif export_type == "trends":
            query, params, db_key = get_inventory_cost_trends(category)
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
