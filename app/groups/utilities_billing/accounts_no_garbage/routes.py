"""
Accounts No Garbage Routes.

This module defines the routes for the Accounts No Garbage report blueprint.
"""

import csv
import logging
from datetime import datetime
from io import StringIO

from flask import Response, jsonify, render_template, request

from app.core.database import execute_query
from app.groups.utilities_billing.accounts_no_garbage import bp
from app.groups.utilities_billing.accounts_no_garbage.queries import (
    get_accounts_no_garbage, get_street_summary)

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
            "groups/utilities_billing/accounts_no_garbage/index.html",
            title="Accounts Without Garbage Service",
        )

    except Exception as e:
        logger.error(f"Error rendering accounts no garbage report index: {str(e)}")
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.

    Returns:
        Response: JSON response with report data.
    """
    try:
        # Get query and parameters
        query, params, db_key = get_accounts_no_garbage()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify({"success": True, "data": results, "count": len(results)})

    except Exception as e:
        logger.error(f"Error fetching accounts no garbage data: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/street-summary")
def get_streets_data():
    """
    Get street summary data as JSON for AJAX requests.

    Returns:
        Response: JSON response with street summary data.
    """
    try:
        # Get query and parameters
        query, params, db_key = get_street_summary()

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Return data as JSON
        return jsonify({"success": True, "data": results, "count": len(results)})

    except Exception as e:
        logger.error(f"Error fetching street summary data: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get query and parameters
        query, params, db_key = get_accounts_no_garbage()

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
        filename = f"accounts_no_garbage_{datetime.now().strftime('%Y%m%d')}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error(f"Error exporting accounts no garbage report: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
