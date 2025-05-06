# app/shared/work_order_comments/routes.py
"""
Work Order Comments Search Routes.

This module defines routes for the shared Work Order Comments Search report.
These routes can be registered with multiple group blueprints.
"""

import logging
import csv
from datetime import datetime, timedelta
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.shared.work_order_comments.queries import (
    get_work_order_comments,
    get_employee_list,
    format_date_for_query,
)

# Configure logger
logger = logging.getLogger(__name__)


def register_work_order_comments_routes(bp, url_prefix="/work_order_comments"):
    """
    Register work order comments search routes with the given blueprint.

    This function adds all the routes needed for the work order comments search report
    to an existing blueprint. This allows the same report to be accessed
    from multiple group sections.

    Args:
        bp (Blueprint): The Flask blueprint to register routes with.
        url_prefix (str): URL prefix for all routes. Defaults to "/work_order_comments".
    """
    logger.info("Registering work order comments routes with blueprint: %s", bp.name)

    # Define the routes as local functions within the registration function

    @bp.route(f"{url_prefix}/")
    def work_order_comments_index():
        """
        Render the main work order comments search report page.

        Returns:
            str: Rendered HTML template.
        """
        try:
            # Default to last 30 days
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            # Get employee list for the dropdown
            query, params, db_key = get_employee_list()
            employees = execute_query(query, params, db_key=db_key)

            return render_template(
                "shared/work_order_comments/index.html",
                title="Work Order Comments Search",
                employees=employees,
                default_start_date=start_date,
                default_end_date=end_date,
                # Include the current group in the template context for breadcrumb navigation
                current_group=bp.name,
            )

        except Exception as e:
            logger.error("Error rendering work order comments report index: %s", str(e))
            return render_template("error.html", error=str(e))

    @bp.route(f"{url_prefix}/search")
    def work_order_comments_search():
        """
        Search for work order comments based on criteria.

        Returns:
            Response: JSON response with matching comments.
        """
        try:
            # Get search parameters
            search_term = request.args.get("search_term", "")
            start_date_str = request.args.get("start_date", "")
            end_date_str = request.args.get("end_date", "")

            # Validate search term
            if not search_term or len(search_term) < 2:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Search term must be at least 2 characters",
                        }
                    ),
                    400,
                )

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
            query, params, db_key = get_work_order_comments(
                search_term, start_date, end_date
            )

            # Execute query
            results = execute_query(query, params, db_key=db_key)

            # Process date fields for JSON serialization
            for row in results:
                if row.get("DATECREATED"):
                    row["DATECREATED"] = (
                        row["DATECREATED"].isoformat()
                        if hasattr(row["DATECREATED"], "isoformat")
                        else row["DATECREATED"]
                    )

                # Create a display name combining first and last name
                if row.get("FIRSTNAME") and row.get("LASTNAME"):
                    row["AUTHOR_NAME"] = f"{row['FIRSTNAME']} {row['LASTNAME']}"
                elif row.get("LASTNAME"):
                    row["AUTHOR_NAME"] = row["LASTNAME"]
                elif row.get("FIRSTNAME"):
                    row["AUTHOR_NAME"] = row["FIRSTNAME"]
                else:
                    row["AUTHOR_NAME"] = "Unknown"

            # Return data as JSON
            return jsonify(
                {
                    "success": True,
                    "data": results,
                    "count": len(results),
                    "filters": {
                        "search_term": search_term,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                    },
                }
            )

        except Exception as e:
            logger.error("Error searching work order comments: %s", str(e))
            return jsonify({"success": False, "error": str(e)}), 500

    @bp.route(f"{url_prefix}/export")
    def export_work_order_comments():
        """
        Export work order comments search results to CSV.

        Returns:
            Response: CSV file download.
        """
        try:
            # Get search parameters
            search_term = request.args.get("search_term", "")
            start_date_str = request.args.get("start_date", "")
            end_date_str = request.args.get("end_date", "")

            # Validate search term
            if not search_term or len(search_term) < 2:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Search term must be at least 2 characters",
                        }
                    ),
                    400,
                )

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
            query, params, db_key = get_work_order_comments(
                search_term, start_date, end_date
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
                    "Author ID",
                    "Author Name",
                    "Comments",
                    "Date Created",
                    "Work Order Description",
                    "Status",
                ]
            )

            # Write data rows
            for row in results:
                # Create author name
                author_name = "Unknown"
                if row.get("FIRSTNAME") and row.get("LASTNAME"):
                    author_name = f"{row['FIRSTNAME']} {row['LASTNAME']}"
                elif row.get("LASTNAME"):
                    author_name = row["LASTNAME"]
                elif row.get("FIRSTNAME"):
                    author_name = row["FIRSTNAME"]

                writer.writerow(
                    [
                        row.get("WORKORDERID", ""),
                        row.get("EMPLOYEEID", ""),
                        author_name,
                        row.get("COMMENTS", ""),
                        row.get("DATECREATED", ""),
                        row.get("DESCRIPTION", ""),
                        row.get("STATUS", ""),
                    ]
                )

            # Create response with CSV file
            output = si.getvalue()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"work_order_comments_{timestamp}.csv"

            return Response(
                output,
                mimetype="text/csv",
                headers={"Content-disposition": f"attachment; filename={filename}"},
            )

        except Exception as e:
            logger.error("Error exporting work order comments: %s", str(e))
            return jsonify({"success": False, "error": str(e)}), 500
