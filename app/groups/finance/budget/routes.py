"""
Budget Dashboard Routes.

This module defines routes for the Budget dashboard.
"""

import logging
from flask import render_template, request, jsonify, Response
from datetime import datetime
import csv
from io import StringIO

from app.core.database import execute_query
from app.groups.finance.budget import bp
from app.groups.finance.budget.queries import (
    get_fiscal_years,
    get_fund_categories,
    get_budget_summary,
    get_monthly_trend,
    get_budget_transactions,
    get_amended_budget_by_fiscal_year,
)

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the Budget dashboard with filter data.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # Get available fiscal years for filters
        years_query, years_params, years_db_key = get_fiscal_years()
        fiscal_years_filter = execute_query(
            years_query, years_params, db_key=years_db_key
        )

        # Get department filter options and filter out None values
        departments_query = """
            SELECT DISTINCT GL_Level_2_Description AS Department 
            FROM vwGL_GLAccount_Full_View 
            WHERE GL_Level_2_Description IS NOT NULL
              AND GL_Level_2_Description <> ''
              AND GL_Level_2_Description <> 'None'
            ORDER BY GL_Level_2_Description
        """
        departments_filter = execute_query(departments_query, (), db_key="nws")

        # Get selected filter values from request
        selected_fiscal_year = request.args.get("fiscal_year", "")
        selected_department = request.args.get("department", "")

        # Validate the selected values
        if selected_fiscal_year and selected_fiscal_year.lower() == "none":
            selected_fiscal_year = ""

        if selected_department and selected_department.lower() == "none":
            selected_department = ""

        logger.info(
            "Rendering Budget dashboard with %d fiscal years and %d departments",
            len(fiscal_years_filter),
            len(departments_filter),
        )

        return render_template(
            "groups/finance/budget/index.html",
            title="Budget Dashboard",
            fiscal_years=fiscal_years_filter,
            departments=departments_filter,
            selected_fiscal_year=selected_fiscal_year,
            selected_department=selected_department,
        )

    except Exception as e:
        logger.error("Error rendering Budget dashboard: %s", str(e))
        return render_template("error.html", error=str(e))


@bp.route("/api/chart-data")
def api_chart_data():
    """
    API endpoint for fetching amended budget chart data.

    Returns:
        Response: JSON response with chart data.
    """
    try:
        # Retrieve filter parameters
        selected_fiscal_year = request.args.get("fiscal_year", "")
        selected_department = request.args.get("department", "")

        # Clean parameters - ensure empty strings become None
        if not selected_fiscal_year or selected_fiscal_year.lower() in ("none", ""):
            selected_fiscal_year = None

        if not selected_department or selected_department.lower() in ("none", ""):
            selected_department = None

        # Log the parameters for debugging
        logger.debug(
            "API Chart Data parameters - fiscal_year: %s, department: %s",
            selected_fiscal_year,
            selected_department,
        )

        # Fetch amended budget data
        query, params, db_key = get_amended_budget_by_fiscal_year(
            selected_fiscal_year, selected_department
        )
        data = execute_query(query, params, db_key=db_key)

        # Check if we have any data
        if not data:
            logger.warning(
                "No budget data found for fiscal_year=%s, department=%s",
                selected_fiscal_year,
                selected_department,
            )
            return jsonify({"success": True, "fiscal_years": [], "amended_totals": []})

        # Process the returned data into lists for the chart
        fiscal_years = [str(row["Fiscal_Year"]) for row in data]  # Ensure strings
        amended_totals = [float(row["AmendedBudget"]) for row in data]

        # Return data for chart
        logger.info("Retrieved %d data points for budget chart", len(fiscal_years))
        return jsonify(
            {
                "success": True,
                "fiscal_years": fiscal_years,
                "amended_totals": amended_totals,
            }
        )

    except Exception as e:
        logger.error("Error generating chart data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/budget-summary")
def api_budget_summary():
    """
    API endpoint to get budget summary data.

    Returns:
        Response: JSON response with budget summary data.
    """
    try:
        fiscal_year = request.args.get("fiscal_year")
        fund_category = request.args.get("fund_category")

        # Validate parameters
        if fiscal_year and fiscal_year.lower() == "none":
            fiscal_year = None

        if fund_category and fund_category.lower() == "none":
            fund_category = None

        # Get data
        query, params, db_key = get_budget_summary(fiscal_year, fund_category)
        data = execute_query(query, params, db_key=db_key)

        # Process data for response
        result = []
        for row in data:
            result.append(
                {
                    "fund": row["Fund"],
                    "department": row["Department"],
                    "division": row["Division"],
                    "total_budget": (
                        float(row["TotalBudget"]) if row["TotalBudget"] else 0
                    ),
                    "total_actual": (
                        float(row["TotalActual"]) if row["TotalActual"] else 0
                    ),
                    "total_encumbrance": (
                        float(row["TotalEncumbrance"]) if row["TotalEncumbrance"] else 0
                    ),
                    "remaining_budget": (
                        float(row["RemainingBudget"]) if row["RemainingBudget"] else 0
                    ),
                    "percent_spent": (
                        float(row["PercentSpent"]) if row["PercentSpent"] else 0
                    ),
                }
            )

        logger.info("Retrieved budget summary with %d rows", len(result))
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error("Error fetching budget summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/monthly-trend")
def api_monthly_trend():
    """
    API endpoint to get monthly trend data.

    Returns:
        Response: JSON response with monthly trend data.
    """
    try:
        fiscal_year = request.args.get("fiscal_year")
        fund = request.args.get("fund")
        department = request.args.get("department")

        # Validate parameters
        if fiscal_year and fiscal_year.lower() == "none":
            fiscal_year = None

        if fund and fund.lower() == "none":
            fund = None

        if department and department.lower() == "none":
            department = None

        # Get data
        query, params, db_key = get_monthly_trend(fiscal_year, fund, department)
        data = execute_query(query, params, db_key=db_key)

        # Process data for response
        result = []
        for row in data:
            result.append(
                {
                    "month": row["Month"],
                    "month_num": row["MonthNum"],
                    "monthly_actual": (
                        float(row["MonthlyActual"]) if row["MonthlyActual"] else 0
                    ),
                    "monthly_budget": (
                        float(row["MonthlyBudget"]) if row["MonthlyBudget"] else 0
                    ),
                    "running_actual": (
                        float(row["RunningActual"]) if row["RunningActual"] else 0
                    ),
                }
            )

        logger.info("Retrieved monthly trend data with %d data points", len(result))
        return jsonify({"success": True, "data": result})

    except Exception as e:
        logger.error("Error fetching monthly trend data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/export")
def export_data():
    """
    Export budget data as CSV.

    Returns:
        Response: CSV file download.
    """
    try:
        fiscal_year = request.args.get("fiscal_year")
        fund_category = request.args.get("fund_category")

        # Validate parameters
        if fiscal_year and fiscal_year.lower() == "none":
            fiscal_year = None

        if fund_category and fund_category.lower() == "none":
            fund_category = None

        # Fetch data
        query, params, db_key = get_budget_summary(fiscal_year, fund_category)
        data = execute_query(query, params, db_key=db_key)

        if not data:
            logger.warning(
                "No data to export with fiscal_year=%s, fund_category=%s",
                fiscal_year,
                fund_category,
            )
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)

        # Write header row
        header = [
            "Fund",
            "Department",
            "Division",
            "Budget",
            "Actual",
            "Encumbrance",
            "Remaining Budget",
            "Percent Spent",
        ]
        writer.writerow(header)

        # Write data rows
        for row in data:
            writer.writerow(
                [
                    row["Fund"],
                    row["Department"],
                    row["Division"],
                    row["TotalBudget"],
                    row["TotalActual"],
                    row["TotalEncumbrance"],
                    row["RemainingBudget"],
                    row["PercentSpent"],
                ]
            )

        # Prepare response
        output.seek(0)

        # Generate filename with date
        filename = f"budget_report_{datetime.now().strftime('%Y%m%d')}.csv"

        logger.info("Exporting budget data to CSV: %s", filename)

        # Return CSV file
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting budget data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
