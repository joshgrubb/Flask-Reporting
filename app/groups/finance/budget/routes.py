# routes.py
"""
Budget Dashboard Routes.

This module defines routes for the Budget dashboard.
"""

import logging
import json
from datetime import datetime
from flask import render_template, request, jsonify, Response
import plotly.graph_objects as go

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


# Main route - just renders the page with filters, no chart generation
@bp.route("/")
def index():
    """
    Render the Budget dashboard with minimal initial data.
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
            return jsonify(
                {
                    "success": True,
                    "fiscal_years": [],
                    "amended_totals": [],
                    "chart_html": "<div class='text-center p-5'>No data available for the selected filters.</div>",
                }
            )

        # Process the returned data into lists for the chart
        fiscal_years = [str(row["Fiscal_Year"]) for row in data]  # Ensure strings
        amended_totals = [float(row["AmendedBudget"]) for row in data]

        # Create the Plotly figure
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=fiscal_years,
                y=amended_totals,
                mode="lines+markers",
                name="Amended Budget",
                marker=dict(
                    size=10,
                    symbol="circle",
                    color="#0D3B66",
                ),
                line=dict(
                    width=3,
                    dash="solid",
                    color="#0D3B66",
                ),
                hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Amended Budget Total by Fiscal Year",
            xaxis_title="Fiscal Year",
            yaxis_title="Amended Budget Total ($)",
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Roboto, sans-serif", size=14, color="#333"),
        )

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=5, label="5Y", step="year", stepmode="backward"),
                        dict(count=10, label="10Y", step="year", stepmode="backward"),
                        dict(step="all"),
                    ]
                )
            ),
        )

        # Generate HTML
        chart_html = fig.to_html(full_html=False, include_plotlyjs=False)

        return jsonify(
            {
                "success": True,
                "chart_html": chart_html,
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
    API endpoint to get budget summary data for charts.

    Returns:
        Response: JSON response with budget summary data.
    """
    try:
        fiscal_year = request.args.get("fiscal_year")
        fund_category = request.args.get("fund_category")

        query, params, db_key = get_budget_summary(fiscal_year, fund_category)
        data = execute_query(query, params, db_key=db_key)

        chart_data = prepare_budget_summary_chart_data(data)

        return jsonify({"success": True, "data": chart_data})

    except Exception as e:
        logger.error("Error fetching budget summary data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/monthly-trend")
def api_monthly_trend():
    """
    API endpoint to get monthly trend data for charts.

    Returns:
        Response: JSON response with monthly trend data.
    """
    try:
        fiscal_year = request.args.get("fiscal_year")
        fund = request.args.get("fund")
        department = request.args.get("department")

        query, params, db_key = get_monthly_trend(fiscal_year, fund, department)
        data = execute_query(query, params, db_key=db_key)

        chart_data = prepare_monthly_trend_chart_data(data)

        return jsonify({"success": True, "data": chart_data})

    except Exception as e:
        logger.error("Error fetching monthly trend data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/budget-transactions")
def api_budget_transactions():
    """
    API endpoint to get detailed budget transactions.

    Returns:
        Response: JSON response with budget transactions.
    """
    try:
        fiscal_year = request.args.get("fiscal_year")
        gl_account = request.args.get("gl_account")

        query, params, db_key = get_budget_transactions(fiscal_year, gl_account)
        data = execute_query(query, params, db_key=db_key)

        return jsonify({"success": True, "data": data})

    except Exception as e:
        logger.error("Error fetching budget transactions: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


def prepare_budget_summary_chart_data(data):
    """
    Prepare data for budget summary charts.

    Args:
        data (list): Budget summary data from database.

    Returns:
        dict: Formatted data for charts.
    """
    funds = []
    departments = []
    budget_values = []
    actual_values = []
    encumbrance_values = []
    remaining_values = []
    percent_spent = []

    for row in data:
        fund_dept = f"{row['Fund']} - {row['Department']}"
        funds.append(row["Fund"])
        departments.append(row["Department"])
        budget_values.append(float(row["TotalBudget"]) if row["TotalBudget"] else 0)
        actual_values.append(float(row["TotalActual"]) if row["TotalActual"] else 0)
        encumbrance_values.append(
            float(row["TotalEncumbrance"]) if row["TotalEncumbrance"] else 0
        )
        remaining_values.append(
            float(row["RemainingBudget"]) if row["RemainingBudget"] else 0
        )
        percent_spent.append(float(row["PercentSpent"]) if row["PercentSpent"] else 0)

    return {
        "funds": funds,
        "departments": departments,
        "budget_values": budget_values,
        "actual_values": actual_values,
        "encumbrance_values": encumbrance_values,
        "remaining_values": remaining_values,
        "percent_spent": percent_spent,
        "fund_department_labels": [f"{f} - {d}" for f, d in zip(funds, departments)],
    }


def prepare_monthly_trend_chart_data(data):
    """
    Prepare data for monthly trend charts.

    Args:
        data (list): Monthly trend data from database.

    Returns:
        dict: Formatted data for charts.
    """
    months = []
    month_nums = []
    monthly_budget = []
    monthly_actual = []
    running_actual = []

    # Sort data by month number
    sorted_data = sorted(data, key=lambda x: x["MonthNum"])

    for row in sorted_data:
        months.append(row["Month"])
        month_nums.append(row["MonthNum"])
        monthly_budget.append(
            float(row["MonthlyBudget"]) if row["MonthlyBudget"] else 0
        )
        monthly_actual.append(
            float(row["MonthlyActual"]) if row["MonthlyActual"] else 0
        )
        running_actual.append(
            float(row["RunningActual"]) if row["RunningActual"] else 0
        )

    return {
        "months": months,
        "monthNum": month_nums,
        "monthly_budget": monthly_budget,
        "monthly_actual": monthly_actual,
        "running_actual": running_actual,
    }


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

        query, params, db_key = get_budget_summary(fiscal_year, fund_category)
        data = execute_query(query, params, db_key=db_key)

        if not data:
            return jsonify({"success": False, "error": "No data to export"}), 404

        # Create CSV in memory
        from io import StringIO
        import csv
        from datetime import datetime

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

        # Return CSV file
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting budget data: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/amended-budget-chart")
def amended_budget_chart():
    """
    Render a page with a Python Plotly line chart showing the amended budget total
    by fiscal year. Filters include fiscal year and department.
    """
    # Retrieve optional filter parameters; empty means "All"
    selected_fiscal_year = request.args.get("fiscal_year", None)
    selected_department = request.args.get("department", None)

    # Fetch amended budget data
    query, params, db_key = get_amended_budget_by_fiscal_year(
        selected_fiscal_year, selected_department
    )
    data = execute_query(query, params, db_key=db_key)

    # Process the returned data into lists for the chart
    fiscal_years = [row["Fiscal_Year"] for row in data]
    amended_totals = [row["AmendedBudget"] for row in data]

    # Create the Plotly line chart
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fiscal_years,
            y=amended_totals,
            mode="lines",
            name="Amended Budget",
            marker=dict(
                size=10,  # Make markers larger
                symbol="circle",  # Choose a symbol that is easy to interpret
                color="#0D3B66",  # Use a pleasant, contrasting color
            ),
            line=dict(
                width=3,  # Increase the line width
                dash="solid",  # Consider using a dash style for variety
                color="#0D3B66",  # Consistent line color matching markers
            ),
            hovertemplate="%{x}: $%{y:,.0f}<extra></extra>",  # Custom hover text
        )
    )

    fig.update_layout(
        title="Amended Budget Total by Fiscal Year",
        xaxis_title="Fiscal Year",
        yaxis_title="Amended Budget Total ($)",
        template="plotly_dark",  # Or another template
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent or custom paper background
        plot_bgcolor="rgba(0,0,0,0)",  # Light gray for a soft contrast
        font=dict(family="Roboto, sans-serif", size=14, color="#333"),
    )

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=5, label="5Y", step="year", stepmode="backward"),
                    dict(count=10, label="10Y", step="year", stepmode="backward"),
                    dict(step="all"),
                ]
            )
        ),
    )

    chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    # Populate fiscal year filter options (you already have this working)
    years_query, years_params, years_db_key = get_fiscal_years()
    fiscal_years_filter = execute_query(years_query, years_params, db_key=years_db_key)

    # Update the query for department filter to use the correct view/column name
    departments_query = """
        SELECT DISTINCT GL_Level_2_Description AS Department 
        FROM vwGL_GLAccount_Full_View 
        ORDER BY GL_Level_2_Description
    """
    departments_filter = execute_query(departments_query, (), db_key="nws")

    # Render the template with the chart and filters
    return render_template(
        "groups/finance/budget/index.html",
        title="Amended Budget Chart",
        chart_html=chart_html,
        fiscal_years=fiscal_years_filter,
        departments=departments_filter,
        selected_fiscal_year=selected_fiscal_year,
        selected_department=selected_department,
    )
