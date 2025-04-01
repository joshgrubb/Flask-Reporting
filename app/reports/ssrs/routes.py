"""
SSRS Module Routes.

This module defines routes for the main SSRS dashboard.
"""

import logging
from flask import render_template, current_app

from app.reports.ssrs import bp

# Configure logger
logger = logging.getLogger(__name__)


@bp.route("/")
def index():
    """
    Render the SSRS reports dashboard.

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
                "url": "/reports/ssrs/new_customer_accounts/",
            }
            # Add more reports as they are implemented
        ]

        # Log that we're rendering the dashboard
        logger.info("Rendering SSRS dashboard with %d reports", len(reports))

        return render_template(
            "ssrs/dashboard.html", title="SSRS Reports Dashboard", reports=reports
        )

    except Exception as e:
        logger.error(f"Error rendering SSRS dashboard: {str(e)}")
        return render_template("error.html", error=str(e))
