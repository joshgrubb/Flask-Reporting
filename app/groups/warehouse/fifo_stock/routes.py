"""
Enhanced FIFO Stock Cost Routes.

This module defines enhanced routes for the FIFO Stock Cost report blueprint,
with support for multiple category selection and improved filtering.
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
    Get list of available inventory categories, excluding blank/null values.

    Returns:
        Response: JSON response with categories data.
    """
    try:
        query, params, db_key = get_inventory_categories()
        results = execute_query(query, params, db_key=db_key)
        categories = [
            row["CATEGORY"]
            for row in results
            if row["CATEGORY"] and row["CATEGORY"].strip()
        ]
        logger.info("Found %d valid category options", len(categories))
        return jsonify({"success": True, "data": categories})
    except Exception as e:
        logger.error("Error fetching inventory categories: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.
    Enhanced to support multiple categories.

    Returns:
        Response: JSON response with report data.
    """
    try:
        category = request.args.get("category", "")
        categories_csv = request.args.get("categories", "")
        categories_list = request.args.getlist("categories[]")

        all_categories = []
        if category:
            all_categories.append(category)
        if categories_csv:
            all_categories.extend([c.strip() for c in categories_csv.split(",")])
        if categories_list:
            all_categories.extend(categories_list)

        unique_categories = []
        for cat in all_categories:
            if cat and cat.strip() and cat.strip() not in unique_categories:
                unique_categories.append(cat.strip())

        if not unique_categories:
            return (
                jsonify(
                    {"success": False, "error": "Please select at least one category"}
                ),
                400,
            )

        all_results = []
        for category in unique_categories:
            query, params, db_key = get_inventory_by_category(category)
            results = execute_query(query, params, db_key=db_key)
            all_results.extend(results)

        logger.info(
            "Processed inventory data for %d categories, found %d items",
            len(unique_categories),
            len(all_results),
        )

        return jsonify(
            {
                "success": True,
                "data": all_results,
                "count": len(all_results),
                "categories": unique_categories,
            }
        )
    except Exception as e:
        logger.error("Error fetching inventory data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/cost-trends")
def get_cost_trends_data():
    """
    Get cost trend data as JSON for AJAX requests.
    Enhanced to support multiple categories and better filtering.

    Returns:
        Response: JSON response with cost trend data.
    """
    try:
        category = request.args.get("category", "")
        categories_csv = request.args.get("categories", "")
        categories_list = request.args.getlist("categories[]")

        all_categories = []
        if category:
            all_categories.append(category)
        if categories_csv:
            all_categories.extend([c.strip() for c in categories_csv.split(",")])
        if categories_list:
            all_categories.extend(categories_list)

        unique_categories = []
        for cat in all_categories:
            if cat and cat.strip() and cat.strip() not in unique_categories:
                unique_categories.append(cat.strip())

        if not unique_categories:
            return (
                jsonify(
                    {"success": False, "error": "Please select at least one category"}
                ),
                400,
            )

        # Get threshold parameter
        threshold_str = request.args.get("threshold", "50")
        try:
            significant_threshold = int(threshold_str)
        except ValueError:
            significant_threshold = 50

        all_results = []
        material_data = {}

        for category_name in unique_categories:
            query, params, db_key = get_inventory_cost_trends(category_name)
            results = execute_query(query, params, db_key=db_key)

            for row in results:
                # Treat null PercentChange as 0 for filtering
                percent_change = (
                    row["PercentChange"] if row["PercentChange"] is not None else 0
                )
                if significant_threshold == 0:
                    # Only flag rows with exactly 0% change (including single price points)
                    row["IsSignificantIncrease"] = abs(percent_change) == 0
                else:
                    row["IsSignificantIncrease"] = (
                        abs(percent_change) >= significant_threshold
                    )
                row["CategoryName"] = category_name
                all_results.append(row)

                material_id = row["MATERIALUID"]
                if material_id not in material_data:
                    material_data[material_id] = []
                material_data[material_id].append(row)

        logger.info(
            "Processed cost trend data for %d categories, found %d records across %d materials",
            len(unique_categories),
            len(all_results),
            len(material_data),
        )

        return jsonify(
            {
                "success": True,
                "data": all_results,
                "materialData": material_data,
                "count": len(all_results),
                "category": ", ".join(unique_categories),
                "categories": unique_categories,
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
    Enhanced to support multiple categories.

    Returns:
        Response: JSON response with summary data.
    """
    try:
        category = request.args.get("category", "")
        categories_csv = request.args.get("categories", "")
        categories_list = request.args.getlist("categories[]")

        all_categories = []
        if category:
            all_categories.append(category)
        if categories_csv:
            all_categories.extend([c.strip() for c in categories_csv.split(",")])
        if categories_list:
            all_categories.extend(categories_list)

        unique_categories = []
        for cat in all_categories:
            if cat and cat.strip() and cat.strip() not in unique_categories:
                unique_categories.append(cat.strip())

        if not unique_categories:
            return (
                jsonify(
                    {"success": False, "error": "Please select at least one category"}
                ),
                400,
            )

        all_results = []
        total_category_value = 0
        total_category_quantity = 0

        for category_name in unique_categories:
            query, params, db_key = get_inventory_summary_by_category(category_name)
            results = execute_query(query, params, db_key=db_key)

            for row in results:
                row["CategoryName"] = category_name
                if row["PercentIncrease"] is None:
                    row["PercentIncrease"] = 0
                all_results.append(row)
                total_category_value += float(row["TotalValue"] or 0)
                total_category_quantity += float(row["TotalQuantity"] or 0)

        logger.info(
            "Processed summary data for %d categories, found %d items",
            len(unique_categories),
            len(all_results),
        )

        return jsonify(
            {
                "success": True,
                "data": all_results,
                "count": len(all_results),
                "category": ", ".join(unique_categories),
                "categories": unique_categories,
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
    Enhanced to support multiple categories.

    Returns:
        Response: CSV file download.
    """
    try:
        category = request.args.get("category", "")
        categories_csv = request.args.get("categories", "")
        categories_list = request.args.getlist("categories[]")

        all_categories = []
        if category:
            all_categories.append(category)
        if categories_csv:
            all_categories.extend([c.strip() for c in categories_csv.split(",")])
        if categories_list:
            all_categories.extend(categories_list)

        unique_categories = []
        for cat in all_categories:
            if cat and cat.strip() and cat.strip() not in unique_categories:
                unique_categories.append(cat.strip())

        if not unique_categories:
            return (
                jsonify(
                    {"success": False, "error": "Please select at least one category"}
                ),
                400,
            )

        export_type = request.args.get(
            "type", "detail"
        )  # 'detail', 'summary' or 'trends'
        all_results = []

        for category_name in unique_categories:
            if export_type == "summary":
                query, params, db_key = get_inventory_summary_by_category(category_name)
            elif export_type == "trends":
                query, params, db_key = get_inventory_cost_trends(category_name)
            else:
                query, params, db_key = get_inventory_by_category(category_name)

            results = execute_query(query, params, db_key=db_key)

            for row in results:
                row["CategoryName"] = category_name
                if export_type == "trends" and row.get("PercentChange") is None:
                    row["PercentChange"] = 0
                if export_type == "summary" and row.get("PercentIncrease") is None:
                    row["PercentIncrease"] = 0
                all_results.append(row)

        if not all_results:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No data found for the selected categories",
                    }
                ),
                404,
            )

        si = StringIO()
        writer = csv.writer(si)
        header = list(all_results[0].keys())
        writer.writerow(header)
        for row in all_results:
            writer.writerow([row.get(key, "") for key in header])

        output = si.getvalue()

        if len(unique_categories) == 1:
            category_str = unique_categories[0]
        elif len(unique_categories) <= 3:
            category_str = "-".join([c.replace(" ", "_") for c in unique_categories])
        else:
            category_str = f"{len(unique_categories)}_categories"

        filename = f"inventory_{category_str}_{export_type}_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        logger.error("Error exporting report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
