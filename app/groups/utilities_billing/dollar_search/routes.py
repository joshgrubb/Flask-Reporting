"""
Dollar Search Routes.

This module defines the routes for the Dollar Search report blueprint.
"""

import logging
import csv
from datetime import datetime
from io import StringIO
from flask import render_template, request, jsonify, Response

from app.core.database import execute_query
from app.groups.utilities_billing.dollar_search import bp
from app.groups.utilities_billing.dollar_search.queries import (
    get_dollar_search,
    get_transaction_count,
    get_default_date_range,
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
        start_date, end_date = get_default_date_range()

        return render_template(
            "groups/utilities_billing/dollar_search/index.html",
            title="Dollar Search Report",
            default_start_date=start_date.strftime("%Y-%m-%d"),
            default_end_date=end_date.strftime("%Y-%m-%d"),
        )

    except Exception as e:
        logger.error("Error rendering Dollar Search report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/search")
def search():
    """
    Search for transactions with a specific dollar amount.

    Returns:
        Response: JSON response with search results.
    """
    try:
        # Get search parameters
        try:
            amount_str = request.args.get("amount", "")
            amount = float(amount_str)
        except ValueError:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid amount format. Please enter a valid dollar amount.",
                    }
                ),
                400,
            )

        # Get date range parameters
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")

        # Parse dates if provided
        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Get query and parameters for transaction data
        query, params, db_key = get_dollar_search(amount, start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Format dates for JSON serialization
        for row in results:
            if row.get("TransactionDate"):
                row["TransactionDate"] = (
                    row["TransactionDate"].isoformat()
                    if hasattr(row["TransactionDate"], "isoformat")
                    else row["TransactionDate"]
                )

        # Get query and parameters for transaction counts
        count_query, count_params, count_db_key = get_transaction_count(
            amount, start_date, end_date
        )

        # Execute count query
        count_results = execute_query(count_query, count_params, db_key=count_db_key)

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": results,
                "counts": count_results,
                "total_count": len(results),
                "filters": {
                    "amount": amount,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                },
            }
        )

    except Exception as e:
        logger.error("Error searching dollar amount: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export():
    """
    Export search results to CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get search parameters
        try:
            amount_str = request.args.get("amount", "")
            amount = float(amount_str)
        except ValueError:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid amount format. Please enter a valid dollar amount.",
                    }
                ),
                400,
            )

        # Get date range parameters
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")

        # Parse dates if provided
        start_date = None
        end_date = None

        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)

        # Get query and parameters
        query, params, db_key = get_dollar_search(amount, start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        # Write header row
        writer.writerow(
            ["Account/Reference", "Amount", "Transaction Date", "Payment Type"]
        )

        # Write data rows
        for row in results:
            # Format amount as currency
            formatted_amount = "${:.2f}".format(float(row["Amount"]))

            # Format date
            transaction_date = row["TransactionDate"]
            if isinstance(transaction_date, datetime):
                formatted_date = transaction_date.strftime("%m/%d/%Y %H:%M:%S")
            else:
                formatted_date = transaction_date

            writer.writerow(
                [
                    row["AccountOrRef"],
                    formatted_amount,
                    formatted_date,
                    row["PaymentType"],
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dollar_search_{amount:.2f}_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting dollar search report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
