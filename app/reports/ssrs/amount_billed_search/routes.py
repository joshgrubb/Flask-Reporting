"""
Amount Billed Search Routes.

This module defines the routes for the Amount Billed Search report blueprint.
"""

import logging
from flask import render_template, request, jsonify

from app.core.database import execute_query
from app.reports.ssrs.amount_billed_search import bp
from app.reports.ssrs.amount_billed_search.queries import get_bill_amount_search

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
            "ssrs/amount_billed_search/index.html", title="Amount Billed Search Report"
        )

    except Exception as e:
        logger.error(f"Error rendering Amount Billed Search report index: {str(e)}")
        return render_template("error.html", error=str(e))


@bp.route("/search")
def search():
    """
    Search for bill amounts matching the criteria.

    Returns:
        Response: JSON response with search results.
    """
    try:
        # Get amount parameter from request
        amount = request.args.get("amount", "")

        if not amount:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Please provide an amount to search for",
                    }
                ),
                400,
            )

        # Get query and parameters
        query, params = get_bill_amount_search(amount)

        # Execute query
        results = execute_query(query, params)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "search_criteria": {"amount": amount},
            }
        )

    except Exception as e:
        logger.error(f"Error searching bill amounts: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export():
    """
    Export search results to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        from flask import Response
        import csv
        from io import StringIO
        from datetime import datetime

        # Get amount parameter from request
        amount = request.args.get("amount", "")

        if not amount:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Please provide an amount to search for",
                    }
                ),
                400,
            )

        # Get query and parameters
        query, params = get_bill_amount_search(amount)

        # Execute query
        results = execute_query(query, params)

        if not results:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "No data found for the specified criteria",
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
        filename = f"bill_amount_search_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Error exporting bill amount search: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
