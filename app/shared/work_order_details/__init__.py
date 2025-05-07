"""
Work Order Details shared module.

This module defines a reusable work order details report that can be
registered with multiple group blueprints while controlling its visibility.
"""

import logging
from flask import Blueprint, render_template, request, jsonify
from app.core.template_helpers import get_blueprint_group_id

# Configure logger
logger = logging.getLogger(__name__)

# Create a shared blueprint (not directly registered with app)
work_order_details_blueprint = Blueprint(
    "work_order_details_shared",
    __name__,
    template_folder="../../templates/shared/work_order_details",
    url_prefix="/work_orders",
)


def register_work_order_details_routes(parent_bp, visible_in=None):
    """
    Register work order details routes with a parent blueprint.

    This function registers the work order details routes with the specified
    parent blueprint and controls visibility in group dashboards.

    Args:
        parent_bp (Blueprint): The parent blueprint to register with
        visible_in (list, optional): List of group IDs where this report should be visible.
                                     If None, visible in parent group only.

    Returns:
        Blueprint: The registered blueprint
    """
    try:
        # Extract the group_id from the parent blueprint
        group_id = get_blueprint_group_id(parent_bp)

        if not group_id:
            logger.warning("Could not determine group_id from parent blueprint")
            group_id = parent_bp.name if hasattr(parent_bp, "name") else "unknown"

        # Register routes with the parent blueprint
        parent_bp.register_blueprint(
            work_order_details_blueprint, url_prefix="/work_orders"
        )

        # Add to report registry with visibility control
        try:
            from app.core.report_registry import register_report

            # If visible_in is not specified, default to this group only
            if visible_in is None:
                visible_in = [group_id]

            # Register the report with specific visibility
            register_report(
                report_id="work_order_search",
                name="Work Order Search",
                url=f"/groups/{group_id}/work_orders/search",
                group_id=group_id,
                description="Search for specific a work order",
                icon="fas fa-search",
                enabled=True,
                visible_in=visible_in,  # Control where this appears in dashboards
            )

            logger.info(
                "Registered work_order_search with %s, visible in %s",
                group_id,
                ", ".join(visible_in),
            )

        except ImportError:
            logger.warning(
                "Could not import report_registry, report will not appear in navigation"
            )
        except Exception as e:
            logger.error("Error registering report with registry: %s", str(e))

        return work_order_details_blueprint

    except Exception as e:
        logger.error("Error registering work_order_details routes: %s", str(e))
        raise


# Define routes on the blueprint
@work_order_details_blueprint.route("/search")
def search():
    """Render the work order search page."""
    try:
        # Get the current group from the request context
        current_group = request.blueprint.split(".")[0]

        # Fallback if the above method fails
        if current_group == "work_order_details_shared":
            # Try to determine the parent group from the URL
            parts = request.path.split("/")
            if len(parts) > 2:
                current_group = parts[2]  # /groups/{group}/work_orders

        return render_template(
            "shared/work_order_details/index.html",
            title="Work Order Search",
            current_group=current_group,
            work_order=None,
            comments=[],
            labor=[],
            materials=[],
            initial_load=True,
            error_message=None,
        )

    except Exception as e:
        logger.error("Error rendering work order search: %s", str(e))
        return render_template("error.html", error=str(e))


@work_order_details_blueprint.route("/<work_order_id>")
def details(work_order_id):
    """
    Display details for a specific work order.

    Args:
        work_order_id (str): The work order ID to display
    """
    try:
        # Get the current group from the request context
        current_group = request.blueprint.split(".")[0]

        # Fallback if the above method fails
        if current_group == "work_order_details_shared":
            # Try to determine the parent group from the URL
            parts = request.path.split("/")
            if len(parts) > 2:
                current_group = parts[2]  # /groups/{group}/work_orders

        # Here you would retrieve the work order details from your database
        # For this example, we'll return a placeholder error

        # Query the database for work order details
        work_order = None  # This would be populated from your database
        comments = []  # This would be populated from your database
        labor = []  # This would be populated from your database
        materials = []  # This would be populated from your database

        error_message = None
        if not work_order:
            error_message = f"Work order {work_order_id} not found"

        return render_template(
            "shared/work_order_details/index.html",
            title=(
                f"Work Order {work_order_id}"
                if not error_message
                else "Work Order Search"
            ),
            current_group=current_group,
            work_order=work_order,
            comments=comments,
            labor=labor,
            materials=materials,
            initial_load=False,
            error_message=error_message,
        )

    except Exception as e:
        logger.error("Error retrieving work order details: %s", str(e))
        return render_template(
            "shared/work_order_details/index.html",
            title="Work Order Search",
            current_group=current_group,
            work_order=None,
            comments=[],
            labor=[],
            materials=[],
            initial_load=False,
            error_message=f"Error: {str(e)}",
        )


@work_order_details_blueprint.route("/api/<work_order_id>")
def api_details(work_order_id):
    """
    API endpoint to get work order details.

    Args:
        work_order_id (str): The work order ID to retrieve
    """
    try:
        # Here you would retrieve the work order details from your database
        # For this example, we'll return a placeholder response

        # Query the database for work order details
        work_order = None  # This would be populated from your database
        comments = []  # This would be populated from your database
        labor = []  # This would be populated from your database
        materials = []  # This would be populated from your database

        if not work_order:
            return (
                jsonify(
                    {"success": False, "error": f"Work order {work_order_id} not found"}
                ),
                404,
            )

        return jsonify(
            {
                "success": True,
                "data": {
                    "work_order": work_order,
                    "comments": comments,
                    "labor": labor,
                    "materials": materials,
                },
            }
        )

    except Exception as e:
        logger.error("Error retrieving work order details via API: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
