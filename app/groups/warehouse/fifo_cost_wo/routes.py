"""
FIFO Work Order Cost Report Routes.

This module defines the routes for the FIFO Work Order Cost report blueprint.
"""

import logging
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, Response
import csv
from io import StringIO

from app.core.database import execute_query
from app.groups.warehouse.fifo_cost_wo import bp
from app.groups.warehouse.fifo_cost_wo.queries import (
    get_fifo_work_order_costs,
    get_work_order_summary,
    format_date_for_query,
    get_default_date_range,
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
        # Get default date range (last complete calendar month)
        start_date, end_date = get_default_date_range()
        default_start_date = start_date.strftime("%Y-%m-%d")
        default_end_date = end_date.strftime("%Y-%m-%d")

        return render_template(
            "groups/warehouse/fifo_cost_wo/index.html",
            title="FIFO Cost by Account Number Report",
            default_start_date=default_start_date,
            default_end_date=default_end_date,
        )

    except Exception as e:
        logger.error("Error rendering FIFO Work Order Cost report index: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/data")
def get_report_data():
    """
    Get report data as JSON for AJAX requests.
    Groups data by Account Number instead of Work Order.

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
            # Use default dates (last complete calendar month)
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=30)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_fifo_work_order_costs(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        # Process the results to group by Account Number
        account_groups = {}

        # Special group for missing account numbers
        missing_acct_key = "MISSING"

        # Process each row
        for row in results:
            # Determine account key (use 'MISSING' for null/empty account numbers)
            acct_num = row["ACCTNUM"]
            acct_key = acct_num if acct_num else missing_acct_key

            # Create account group if it doesn't exist
            if acct_key not in account_groups:
                account_groups[acct_key] = {
                    "ACCTNUM": acct_key,
                    "ITEMS": [],
                    "TOTAL_COST": 0,
                    "WORK_ORDERS": set(),  # Use a set to avoid duplicates
                    "IS_MISSING": acct_key == missing_acct_key,
                }

            # Add the item
            account_groups[acct_key]["ITEMS"].append(
                {
                    "WORKORDERID": row["WORKORDERID"],
                    "MATERIALUID": row["MATERIALUID"],
                    "DESCRIPTION": row["DESCRIPTION"],
                    "UNITSREQUIRED": row["UNITSREQUIRED"],
                    "COST": row["COST"],
                    "TRANSDATE": row["TRANSDATE"],
                    "WOCATEGORY": row["WOCATEGORY"],
                }
            )

            # Add work order to set
            account_groups[acct_key]["WORK_ORDERS"].add(row["WORKORDERID"])

            # Add to total cost
            account_groups[acct_key]["TOTAL_COST"] += float(row["COST"] or 0)

        # Convert work order sets to counts and convert to list for JSON
        account_list = []
        for acct in account_groups.values():
            acct["WORK_ORDER_COUNT"] = len(acct["WORK_ORDERS"])
            acct["ITEM_COUNT"] = len(acct["ITEMS"])
            # Convert set to list for serialization
            acct["WORK_ORDERS"] = list(acct["WORK_ORDERS"])
            account_list.append(acct)

        # Sort by cost (descending) with missing accounts at the top
        account_list.sort(key=lambda x: (0 if x["IS_MISSING"] else 1, -x["TOTAL_COST"]))

        # Return data as JSON
        return jsonify(
            {
                "success": True,
                "data": account_list,
                "count": len(account_list),
                "filters": {
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error fetching work order cost data: %s", str(e))
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
            # Use default dates
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=30)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_work_order_summary(start_date, end_date)

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
        logger.error("Error fetching summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_report():
    """
    Export report data to CSV.
    Supports detailed, summary, and template export formats.

    Returns:
        Response: CSV file download.
    """
    try:
        # Get date filters and export type from request
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")
        export_type = request.args.get(
            "type", "detail"
        )  # 'detail', 'summary', or 'template'

        # Parse dates if provided
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0)

            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)
        else:
            # Use default dates
            end_date = datetime.now().replace(hour=23, minute=59, second=59)
            start_date = (end_date - timedelta(days=30)).replace(
                hour=0, minute=0, second=0
            )

        # Get query and parameters
        query, params, db_key = get_fifo_work_order_costs(start_date, end_date)

        # Execute query
        results = execute_query(query, params, db_key=db_key)

        if not results:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV file in memory
        si = StringIO()
        writer = csv.writer(si)

        if export_type == "detail":
            # Detailed export - all items
            # Write header row for detailed export
            writer.writerow(
                [
                    "Account Number",
                    "Work Order ID",
                    "Category",
                    "Material ID",
                    "Description",
                    "Units",
                    "Cost",
                    "Transaction Date",
                ]
            )

            # Write data rows organized by account number
            for row in results:
                acct_num = row["ACCTNUM"] if row["ACCTNUM"] else "MISSING"
                writer.writerow(
                    [
                        acct_num,
                        row["WORKORDERID"],
                        row["WOCATEGORY"],
                        row["MATERIALUID"],
                        row["DESCRIPTION"],
                        row["UNITSREQUIRED"],
                        row["COST"],
                        row["TRANSDATE"],
                    ]
                )

            filename = (
                f"fifo_cost_by_account_detail_{datetime.now().strftime('%Y%m%d')}.csv"
            )
        elif export_type == "summary":
            # Summary export - totals per account
            # Process the results to group by Account Number
            account_groups = {}

            # Process each row
            for row in results:
                # Determine account key (use 'MISSING' for null/empty account numbers)
                acct_num = row["ACCTNUM"]
                acct_key = acct_num if acct_num else "MISSING"

                # Create account group if it doesn't exist
                if acct_key not in account_groups:
                    account_groups[acct_key] = {
                        "ACCTNUM": acct_key,
                        "TOTAL_COST": 0,
                        "ITEM_COUNT": 0,
                        "WORK_ORDERS": set(),
                    }

                # Add to group
                account_groups[acct_key]["TOTAL_COST"] += float(row["COST"] or 0)
                account_groups[acct_key]["ITEM_COUNT"] += 1
                account_groups[acct_key]["WORK_ORDERS"].add(row["WORKORDERID"])

            # Write header row for summary export
            writer.writerow(
                ["Account Number", "Total Cost", "Item Count", "Work Order Count"]
            )

            # Write account summary rows
            for acct_key, account in account_groups.items():
                writer.writerow(
                    [
                        acct_key,
                        account["TOTAL_COST"],
                        account["ITEM_COUNT"],
                        len(account["WORK_ORDERS"]),
                    ]
                )

            filename = (
                f"fifo_cost_by_account_summary_{datetime.now().strftime('%Y%m%d')}.csv"
            )
        else:  # template export
            # G/L Template export - formatted for G/L import
            # Process the results to group by Account Number
            account_groups = {}

            # Process each row
            for row in results:
                # Skip rows with missing account numbers
                if not row["ACCTNUM"]:
                    continue

                acct_num = row["ACCTNUM"]

                # Create account group if it doesn't exist
                if acct_num not in account_groups:
                    account_groups[acct_num] = {"ACCTNUM": acct_num, "TOTAL_COST": 0}

                # Add to group total
                account_groups[acct_num]["TOTAL_COST"] += float(row["COST"] or 0)

            # Write header row for template export
            writer.writerow(
                [
                    "G/L Date",
                    "G/L Account",
                    "Amount",
                    "Description",
                    "Source",
                    "Due To/Due From Fund",
                    "Org",
                    "Set",
                    "ProjCode1",
                    "ProjCode2",
                    "PrjCode3",
                    "Sub Ledger Type",
                    "Sub Ledger Description",
                ]
            )

            # Use the end date for all rows
            gl_date = end_date.strftime("%m/%d/%Y")

            # Write account rows
            for acct_num, account in account_groups.items():
                writer.writerow(
                    [
                        gl_date,  # G/L Date
                        account["ACCTNUM"],  # G/L Account
                        account["TOTAL_COST"],  # Amount
                        "",  # Description
                        "Cityworks",  # Source
                        "",  # Due To/Due From Fund
                        "",  # Org
                        "",  # Set
                        "",  # ProjCode1
                        "",  # ProjCode2
                        "",  # PrjCode3
                        "",  # Sub Ledger Type
                        "",  # Sub Ledger Description
                    ]
                )

            filename = f"cityworks_gl_template_{end_date.strftime('%Y%m%d')}.csv"

        # Create response with CSV file
        output = si.getvalue()

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting report: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
