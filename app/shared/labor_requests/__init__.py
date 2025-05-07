"""
Labor Requests shared module.

This module defines a reusable labor requests report that can be
registered with multiple group blueprints while controlling its visibility.
"""

import logging
from flask import Blueprint, render_template, request
from app.core.template_helpers import get_blueprint_group_id

# Configure logger
logger = logging.getLogger(__name__)

# Create a shared blueprint (not directly registered with app)
labor_requests_blueprint = Blueprint(
    "labor_requests_shared",
    __name__,
    template_folder="../../templates/shared/labor_requests",
)


def register_labor_requests_routes(parent_bp, visible_in=None):
    """
    Register labor requests routes with a parent blueprint.

    This function registers the labor requests routes with the specified
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

        # Determine route prefix
        url_prefix = "/labor_requests"

        # Register routes with the parent blueprint
        parent_bp.register_blueprint(labor_requests_blueprint, url_prefix=url_prefix)

        # Add to report registry with visibility control
        try:
            from app.core.report_registry import register_report

            # If visible_in is not specified, default to this group only
            if visible_in is None:
                visible_in = [group_id]

            # Register the report with specific visibility
            register_report(
                report_id="labor_requests",
                name="Labor Requests",
                url=f"/groups/{group_id}/labor_requests/",
                group_id=group_id,
                description="View and analyze service requests labor by category and date range",
                icon="fas fa-hard-hat",
                enabled=True,
                visible_in=visible_in,  # Control where this appears in dashboards
            )

            logger.info(
                "Registered labor_requests with %s, visible in %s",
                group_id,
                ", ".join(visible_in),
            )

        except ImportError:
            logger.warning(
                "Could not import report_registry, report will not appear in navigation"
            )
        except Exception as e:
            logger.error("Error registering report with registry: %s", str(e))

        return labor_requests_blueprint

    except Exception as e:
        logger.error("Error registering labor_requests routes: %s", str(e))
        raise


# Define routes on the blueprint
@labor_requests_blueprint.route("/")
def index():
    """Render the labor requests report page."""
    try:
        # Get the current group from the request context
        current_group = request.blueprint.split(".")[0]

        # Fallback if the above method fails
        if current_group == "labor_requests_shared":
            # Try to determine the parent group from the URL
            parts = request.path.split("/")
            if len(parts) > 2:
                current_group = parts[2]  # /groups/{group}/labor_requests

        # Get default dates (last 30 days)
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        # Get available categories from database
        categories = []  # You would populate this from your database

        return render_template(
            "shared/labor_requests/index.html",
            title="Service Requests Labor",
            default_start_date=start_date,
            default_end_date=end_date,
            categories=categories,
            current_group=current_group,
        )

    except Exception as e:
        logger.error("Error rendering labor requests report: %s", str(e))
        return render_template("error.html", error=str(e))


# Additional routes would go here
@labor_requests_blueprint.route("/data")
def get_data():
    """API endpoint to get labor data."""
    # Implementation would go here
    pass


@labor_requests_blueprint.route("/export")
def export_data():
    """API endpoint to export labor data as CSV."""
    # Implementation would go here
    pass
