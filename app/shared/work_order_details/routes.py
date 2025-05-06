"""
Work Order Details Routes.

This module defines routes for the shared Work Order Details view.
These routes can be registered with multiple group blueprints.
"""

import logging
from flask import render_template, request, jsonify, abort

from app.core.database import execute_query
from app.shared.work_order_details.queries import (
    get_work_order_details,
    get_work_order_comments,
    get_work_order_labor,
)

# Configure logger
logger = logging.getLogger(__name__)


def register_work_order_details_routes(bp, url_prefix="/work_orders"):
    """
    Register work order details routes with the given blueprint.

    This function adds all the routes needed for the work order details view
    to an existing blueprint. This allows the same view to be accessed
    from multiple group sections.

    Args:
        bp (Blueprint): The Flask blueprint to register routes with.
        url_prefix (str): URL prefix for all routes. Defaults to "/work_orders".
    """
    logger.info("Registering work order details routes with blueprint: %s", bp.name)

    @bp.route(f"{url_prefix}/<work_order_id>")
    def work_order_details(work_order_id):
        """
        Display details for a specific work order.

        Args:
            work_order_id (str): The ID of the work order to view.

        Returns:
            str: Rendered HTML template.
        """
        try:
            # Get work order details
            details_query, details_params, details_db_key = get_work_order_details(
                work_order_id
            )
            details = execute_query(
                details_query, details_params, fetch_all=False, db_key=details_db_key
            )

            if not details:
                logger.warning("Work order not found: %s", work_order_id)
                abort(404, description=f"Work order {work_order_id} not found")

            # Get work order comments
            comments_query, comments_params, comments_db_key = get_work_order_comments(
                work_order_id
            )
            comments = execute_query(
                comments_query, comments_params, db_key=comments_db_key
            )

            # Get work order labor
            labor_query, labor_params, labor_db_key = get_work_order_labor(
                work_order_id
            )
            labor = execute_query(labor_query, labor_params, db_key=labor_db_key)

            # Format author names for comments
            for comment in comments:
                if comment.get("FIRSTNAME") and comment.get("LASTNAME"):
                    comment["AUTHOR_NAME"] = (
                        f"{comment['FIRSTNAME']} {comment['LASTNAME']}"
                    )
                elif comment.get("LASTNAME"):
                    comment["AUTHOR_NAME"] = comment["LASTNAME"]
                elif comment.get("FIRSTNAME"):
                    comment["AUTHOR_NAME"] = comment["FIRSTNAME"]
                else:
                    comment["AUTHOR_NAME"] = "Unknown"

            # Format labor names
            for entry in labor:
                if entry.get("FIRSTNAME") and entry.get("LASTNAME"):
                    entry["EMPLOYEE_NAME"] = f"{entry['FIRSTNAME']} {entry['LASTNAME']}"
                elif entry.get("LASTNAME"):
                    entry["EMPLOYEE_NAME"] = entry["LASTNAME"]
                elif entry.get("FIRSTNAME"):
                    entry["EMPLOYEE_NAME"] = entry["FIRSTNAME"]
                else:
                    entry["EMPLOYEE_NAME"] = "Unknown"

            return render_template(
                "shared/work_order_details/index.html",
                title=f"Work Order {work_order_id}",
                work_order=details,
                comments=comments,
                labor=labor,
                current_group=bp.name,
            )

        except Exception as e:
            logger.error("Error retrieving work order details: %s", str(e))
            return render_template("error.html", error=str(e))

    # Define a search route for work orders
    @bp.route(f"{url_prefix}/search")
    def work_order_search():
        """
        Search for work orders based on criteria.

        Returns:
            str: Rendered HTML template with search form.
        """
        try:
            return render_template(
                "shared/work_order_details/search.html",
                title="Search Work Orders",
                current_group=bp.name,
            )
        except Exception as e:
            logger.error("Error rendering work order search page: %s", str(e))
            return render_template("error.html", error=str(e))
