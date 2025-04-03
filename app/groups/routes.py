"""
Utilities Billing Group Routes.

This module defines routes for the Utilities Billing group dashboard.
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
                "icon": "fas fa-home",
            },
            {
                "id": "accounts_no_garbage",
                "name": "Accounts Without Garbage Service",
                "description": "Report showing residential accounts without garbage service",
                "url": "/groups/utilities_billing/accounts_no_garbage/",
                "icon": "fas fa-trash-alt",
            },
            {
                "id": "amount_billed_search",
                "name": "Amount Billed Search",
                "description": "Search for bill amounts in the system",
                "url": "/groups/utilities_billing/amount_billed_search/",
                "icon": "fas fa-search-dollar",
            },
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info(
            "Rendering Utilities Billing dashboard with %d reports", len(reports)
        )

        return render_template(
            "groups/utilities_billing/dashboard.html",
            title="Utilities Billing Reports",
            reports=reports,
        )

    except Exception as e:
        logger.error(f"Error rendering Utilities Billing dashboard: {str(e)}")
        return render_template("error.html", error=str(e))
