"""
Labor Requests Routes.

This module defines routes for the shared Labor Requests report.
These routes can be registered with multiple group blueprints.
"""

import logging
import csv
from datetime import datetime, timedelta
from io import StringIO
from flask import render_template, request, jsonify, Response, url_for

from app.core.database import execute_query
from app.shared.labor_requests.queries import (
    get_labor_requests,
    get_request_categories,
    format_date_for_query,
)

# Configure logger
logger = logging.getLogger(__name__)


def register_labor_requests_routes(bp, url_prefix="/labor_requests"):
    """
    Register labor requests routes with the given blueprint.

    This function adds all the routes needed for the labor requests report
    to an existing blueprint. This allows the same report to be accessed
    from multiple group sections.

    Args:
        bp (Blueprint): The Flask blueprint to register routes with.
        url_prefix (str): URL prefix for all routes. Defaults to "/labor_requests".
    """
    logger.info("Registering labor requests routes with blueprint: %s", bp.name)

    # Define the routes as local functions within the registration function

    @bp.route(f"{url_prefix}/")
    def labor_requests_index():
        """
        Render the main labor requests report page.
    
        Returns:
            str: Rendered HTML template.
        """
        try:
            # Default to last 30 days
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
            # Get categories for the dropdown
            query, params, db_key = get_request_categories()
            
            # Get actual categories from database
            categories = execute_query(query, params, db_key=db_key)
    
            return render_template(
                "shared/labor_requests/index.html",
                title="Labor Requests Report",
                categories=categories,
                default_start_date=start_date,
                default_end_date=end_date,
                # Include the current group in the template context for breadcrumb navigation
                current_group=bp.name,
            )
    
        except Exception as e:
            logger.error("Error rendering labor requests report index: %s", str(e))
            return render_template("error.html", error=str(e))

    @bp.route(f"{url_prefix}/data")
    def labor_requests_data():
        """
        Get labor requests data as JSON for AJAX requests.

        Returns:
            Response: JSON response with labor requests data.
        """
        try:
            # Get date filters and category from request
            start_date_str = request.args.get("start_date", "")
            end_date_str = request.args.get("end_date", "")
            category = request.args.get("category", "")

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
            query, params, db_key = get_labor_requests(
                start_date, end_date, category if category else None
            )

            # Execute query to get real data from database
            results = execute_query(query, params, db_key=db_key)

            # Process date fields for JSON serialization
            for row in results:
                if row.get("TRANSDATE"):
                    row["TRANSDATE"] = (
                        row["TRANSDATE"].isoformat()
                        if hasattr(row["TRANSDATE"], "isoformat")
                        else row["TRANSDATE"]
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
                        "category": category,
                    },
                }
            )

        except Exception as e:
            logger.error("Error fetching labor requests data: %s", str(e))
            return jsonify({"success": False, "error": str(e)}), 500

    @bp.route(f"{url_prefix}/export")
    def export_labor_requests():
        """
        Export labor requests data to CSV.

        Returns:
            Response: CSV file download.
        """
        try:
            # Get date filters and category from request
            start_date_str = request.args.get("start_date", "")
            end_date_str = request.args.get("end_date", "")
            category = request.args.get("category", "")

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
            query, params, db_key = get_labor_requests(
                start_date, end_date, category if category else None
            )

            # Execute query to get real data from database
            results = execute_query(query, params, db_key=db_key)

            if not results:
                return jsonify({"success": False, "error": "No data to export"}), 404

            # Create CSV file in memory
            si = StringIO()
            writer = csv.writer(si)

            # Write header row
            writer.writerow(
                [
                    "Request ID",
                    "Labor Name",
                    "Hours",
                    "Cost",
                    "Transaction Date",
                    "Description",
                    "Category",
                ]
            )

            # Write data rows
            for row in results:
                writer.writerow(
                    [
                        row.get("REQUESTID", ""),
                        row.get("LABORNAME", ""),
                        row.get("HOURS", ""),
                        row.get("COST", ""),
                        row.get("TRANSDATE", ""),
                        row.get("DESCRIPTION", ""),
                        row.get("REQCATEGORY", ""),
                    ]
                )

            # Create response with CSV file
            output = si.getvalue()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"labor_requests_{timestamp}.csv"

            return Response(
                output,
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename={filename}"},
            )

        except Exception as e:
            logger.error("Error exporting labor requests: %s", str(e))
            return jsonify({"success": False, "error": str(e)}), 500
