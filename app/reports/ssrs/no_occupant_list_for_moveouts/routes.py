"""
No Occupant List for Moveouts Routes.

This module defines the routes for the No Occupant List for Moveouts report blueprint.
"""

import logging
from datetime import datetime, timedelta
from flask import render_template, request, jsonify

from app.core.database import execute_query
from app.reports.ssrs.no_occupant_list_for_moveouts import bp
from app.reports.ssrs.no_occupant_list_for_moveouts.queries import (
    get_moveouts_without_occupants,
    get_moveouts_summary,
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
        # Default to last 90 days
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        return render_template(
            "ssrs/no_occupant_list_for_moveouts/index.html",
            title="No Occupant List for Moveouts Report",
            default_start_date=start_date,
            default_end_date=end_date,
        )

    except Exception as e:
        logger.error(f"Error rendering report index: {str(e)}")
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
            # Use default dates (last 90 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=90)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_moveouts_without_occupants(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error fetching report data: {str(e)}")
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
            # Use default dates (last 90 days)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=90)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_moveouts_summary(start_date, end_date)

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
        logger.error(f"Error fetching summary data: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        from flask import Response
        import csv
        from io import StringIO

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
        query, params, db_key = get_moveouts_without_occupants(start_date, end_date)

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
        filename = (
            f"no_occupant_list_for_moveouts_{datetime.now().strftime('%Y%m%d')}.csv"
        )

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
