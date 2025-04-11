"""
Utilities Billing Module Routes.

This module defines routes for the main Utilities Billing dashboard.
"""

import logging
from flask import render_template, current_app

from app.groups.utilities_billing import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the Utilities Billing reports dashboard.

    Returns:
        str: Rendered HTML template.
    """
    try:
        # List of available reports
        reports = [
            {
                "id": "utility_dashboard",
                "name": "Utility Billing Dashboard",
                "description": "Overview of utility billing metrics and KPIs",
                "url": "/groups/utilities_billing/trending/",
                "icon": "fa-solid fa-chart-column",
            },
            {
                "id": "new_customer_accounts",
                "name": "New Customer Accounts",
                "description": "Report showing new customer account information",
                "url": "/groups/utilities_billing/new_customer_accounts/",
                "icon": "fas fa-user-plus",
            },
            {
                "id": "no_occupant_list_for_moveouts",
                "name": "No Occupant List for Moveouts",
                "description": "Report showing addresses with moveouts that have no new occupants",
                "url": "/groups/utilities_billing/no_occupant_list_for_moveouts/",
                "icon": "fa-solid fa-building-circle-arrow-right",
            },
            {
                "id": "accounts_no_garbage",
                "name": "Accounts Without Garbage Service",
                "description": "Report showing residential accounts without garbage service",
                "url": "/groups/utilities_billing/accounts_no_garbage/",
                "icon": "fa-solid fa-trash",
            },
            {
                "id": "amount_billed_search",
                "name": "Amount Billed Search",
                "description": "Search for bill amounts in the system",
                "url": "/groups/utilities_billing/amount_billed_search/",
                "icon": "fas fa-search-dollar",
            },
            {
                "id": "cash_only_accounts",
                "name": "Cash Only Accounts",
                "description": "Utility accounts restricted to cash only, no checks",
                "url": "/groups/utilities_billing/cash_only_accounts/",
                "icon": "fa-solid fa-money-bill-1",
            },
            {
                "id": "vflex",
                "name": "VFLEX for Sensus",
                "description": "VFLEX file to upload to Sensus to update customer data.",
                "url": "/groups/utilities_billing/vflex/",
                "icon": "fa-solid fa-users",
            },
            {
                "id": "credit_balance",
                "name": "Credit Balance Report",
                "description": "View accounts with credit balances (negative balance amounts)",
                "url": "/groups/utilities_billing/credit_balance/",
                "icon": "fas fa-dollar-sign",
            },
            {
                "id": "cut_nonpayment",
                "name": "Cut for Nonpayment",
                "description": "View accounts being cut for nonpayment",
                "url": "/groups/utilities_billing/cut_nonpayment/",
                "icon": "fas fa-cut",
            },
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering Utilities Billing dashboard with %d reports", len(reports))

        return render_template(
            "utilities_billing/dashboard.html", title="Utilities Billing Reports Dashboard", reports=reports
        )

    except Exception as e:
        logger.error(f"Error rendering Utilities Billing dashboard: {str(e)}")
        return render_template("error.html", error=str(e))
