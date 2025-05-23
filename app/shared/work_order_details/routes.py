"""
Work Order Details Routes.

This module defines routes for the shared Work Order Details view.
These routes can be registered with multiple group blueprints.
"""

import logging
from flask import render_template, request, jsonify, abort, redirect, url_for

from app.core.database import execute_query
from app.shared.work_order_details.queries import (
    get_work_order_details,
    get_work_order_comments,
    get_work_order_labor,
    get_work_order_materials,
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

    @bp.route(f"{url_prefix}/")
    def work_order_index():
        """
        Main work order route.

        When accessed without a work order ID, it displays the default view
        with a search form.

        Returns:
            str: Rendered HTML template.
        """
        try:
            return render_template(
                "shared/work_order_details/index.html",
                title="Work Orders",
                work_order=None,  # No work order details
                comments=[],  # Empty comments
                labor=[],  # Empty labor
                materials=[],  # Empty materials
                current_group=bp.name,
                initial_load=True,  # Flag to indicate this is the initial page load
            )
        except Exception as e:
            logger.error("Error rendering work order index: %s", str(e))
            return render_template("error.html", error=str(e))

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
                # This is a search that returned no results, not an initial page load
                return render_template(
                    "shared/work_order_details/index.html",
                    title="Work Orders",
                    work_order=None,
                    comments=[],
                    labor=[],
                    materials=[],
                    current_group=bp.name,
                    initial_load=False,  # Not an initial load
                    error_message=f"Work order {work_order_id} not found",
                )

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

            # Get work order materials
            materials_query, materials_params, materials_db_key = (
                get_work_order_materials(work_order_id)
            )
            materials = execute_query(
                materials_query, materials_params, db_key=materials_db_key
            )

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
                materials=materials,
                current_group=bp.name,
                initial_load=False,  # Not an initial load
            )

        except Exception as e:
            logger.error("Error retrieving work order details: %s", str(e))
            return render_template("error.html", error=str(e))
