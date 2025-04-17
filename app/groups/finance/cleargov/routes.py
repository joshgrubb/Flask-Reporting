# app/groups/finance/cleargov/routes.py
"""
ClearGov Budget Reports Routes.

This module defines routes for the ClearGov budget visualization reports.
"""

import logging
from flask import render_template

from app.groups.finance.cleargov import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the ClearGov budget visualization report.

    Returns:
        str: Rendered HTML template.
    """
    try:
        logger.info("Rendering ClearGov budget reports")

        # Define the widgets to be displayed
        widgets = [
            {
                "name": "total_expenditures",
                "id": "cleargov-widget-zpbmwv",
                "script_src": "https://cleargov.com/widget/zpbmwv",
                "title": "Total Expenditures",
                "description": "Overview of total town expenditures",
            },
            {
                "name": "fund_expenses",
                "id": "cleargov-widget-yenklmpi",
                "script_src": "https://cleargov.com/widget/yenklmpi",
                "title": "Fund Expenses",
                "description": "Expenses broken down by fund through December 2024",
            },
            {
                "name": "cost_recovery_rate",
                "id": "cleargov-widget-sgqqfzwk",
                "script_src": "https://cleargov.com/widget/sgqqfzwk",
                "title": "Cost Recovery Rate",
                "description": "Analysis of cost recovery for town services",
            },
            {
                "name": "expenses_by_fund",
                "id": "cleargov-widget-ohdmvi",
                "script_src": "https://cleargov.com/widget/ohdmvi",
                "title": "Expenses by Fund",
                "description": "Detailed breakdown of expenses by fund category",
            },
            {
                "name": "budget_by_department",
                "id": "cleargov-widget-gvtgfy",
                "script_src": "https://cleargov.com/widget/gvtgfy",
                "title": "Budget by Department",
                "description": "Departmental budget allocation and spending",
            },
            {
                "name": "ad_valorem",
                "id": "cleargov-widget-dwvjkb",
                "script_src": "https://cleargov.com/widget/dwvjkb",
                "title": "65¢ Ad Valorem",
                "description": "Ad Valorem tax distribution and utilization",
            },
            {
                "name": "fire_personnel_budget",
                "id": "cleargov-widget-deeymh",
                "script_src": "https://cleargov.com/widget/deeymh",
                "title": "Fire Personnel Budget",
                "description": "Budget allocation for fire department personnel",
            },
        ]

        return render_template(
            "groups/finance/cleargov/index.html",
            title="ClearGov Budget Visualizations",
            widgets=widgets,
        )

    except Exception as e:
        logger.error("Error rendering ClearGov reports: %s", str(e))
        return render_template("error.html", error=str(e))
