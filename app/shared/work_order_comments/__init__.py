"""
Work Order Comments shared module.

This module defines a reusable work order comments search report that can be
registered with multiple group blueprints while controlling its visibility.
"""

import logging
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, Response
from app.core.template_helpers import get_blueprint_group_id

# Configure logger
logger = logging.getLogger(__name__)

# Create a shared blueprint (not directly registered with app)
work_order_comments_blueprint = Blueprint(
    "work_order_comments_shared",
    __name__,
    template_folder="../../templates/shared/work_order_comments",
)


def register_work_order_comments_routes(parent_bp, visible_in=None):
    """
    Register work order comments routes with a parent blueprint.

    This function registers the work order comments search routes with the specified
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
        url_prefix = "/work_order_comments"

        # Register routes with the parent blueprint
        parent_bp.register_blueprint(
            work_order_comments_blueprint, url_prefix=url_prefix
        )

        # Add to report registry with visibility control
        try:
            from app.core.report_registry import register_report

            # If visible_in is not specified, default to this group only
            if visible_in is None:
                visible_in = [group_id]

            # Register the report with specific visibility
            register_report(
                report_id="work_order_comments",
                name="Work Order Comments Search",
                url=f"/groups/{group_id}/work_order_comments/",
                group_id=group_id,
                description="Search for specific text within work order comments",
                icon="fas fa-search",
                enabled=True,
                visible_in=visible_in,  # Control where this appears in dashboards
            )

            logger.info(
                "Registered work_order_comments with %s, visible in %s",
                group_id,
                ", ".join(visible_in),
            )

        except ImportError:
            logger.warning(
                "Could not import report_registry, report will not appear in navigation"
            )
        except Exception as e:
            logger.error("Error registering report with registry: %s", str(e))

        return work_order_comments_blueprint

    except Exception as e:
        logger.error("Error registering work_order_comments routes: %s", str(e))
        raise


# Define routes on the blueprint
@work_order_comments_blueprint.route("/")
def index():
    """Render the work order comments search page."""
    try:
        # Get the current group from the request context
        current_group = request.blueprint.split(".")[0]

        # Fallback if the above method fails
        if current_group == "work_order_comments_shared":
            # Try to determine the parent group from the URL
            parts = request.path.split("/")
            if len(parts) > 2:
                current_group = parts[2]  # /groups/{group}/work_order_comments

        # Get default dates (last 30 days)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        return render_template(
            "shared/work_order_comments/index.html",
            title="Work Order Comments Search",
            default_start_date=start_date,
            default_end_date=end_date,
            current_group=current_group,
            initial_load=True,
        )

    except Exception as e:
        logger.error("Error rendering work order comments search: %s", str(e))
        return render_template("error.html", error=str(e))


@work_order_comments_blueprint.route("/search")
def search_comments():
    """API endpoint to search work order comments."""
    try:
        # Get search parameters
        search_term = request.args.get("search_term", "")
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")

        # Validate parameters
        if not search_term or len(search_term) < 2:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Search term is required (min 2 characters)",
                    }
                ),
                400,
            )

        # Process dates with proper error handling
        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                start_date = start_date.replace(hour=0, minute=0, second=0)
            else:
                start_date = (datetime.now() - timedelta(days=30)).replace(
                    hour=0, minute=0, second=0
                )

            if end_date_str:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                end_date = end_date.replace(hour=23, minute=59, second=59)
            else:
                end_date = datetime.now().replace(hour=23, minute=59, second=59)
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format"}), 400

        # Here you would implement your database query to search comments
        # For this example, we'll return a placeholder response
        results = []  # This would be populated from your database

        return jsonify(
            {
                "success": True,
                "data": results,
                "count": len(results),
                "filters": {
                    "search_term": search_term,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                },
            }
        )

    except Exception as e:
        logger.error("Error searching work order comments: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@work_order_comments_blueprint.route("/export")
def export_comments():
    """API endpoint to export search results as CSV."""
    try:
        # Get search parameters
        search_term = request.args.get("search_term", "")
        start_date_str = request.args.get("start_date", "")
        end_date_str = request.args.get("end_date", "")

        # Validate parameters
        if not search_term or len(search_term) < 2:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Search term is required (min 2 characters)",
                    }
                ),
                400,
            )

        # Process dates with proper error handling
        # (Similar to search_comments function)

        # Here you would implement your database query to get the data for export
        # For this example, we'll return a placeholder error

        # Create CSV file in memory (assuming you have results)
        results = []  # This would be populated from your database

        if not results:
            return jsonify({"success": False, "error": "No data found for export"}), 404

        # Example CSV generation code (would be customized for your actual data)
        import csv
        from io import StringIO

        si = StringIO()
        writer = csv.writer(si)

        # Write header row
        writer.writerow(
            ["Work Order ID", "Description", "Status", "Author", "Comment", "Date"]
        )

        # Write data rows
        for row in results:
            writer.writerow(
                [
                    row.get("work_order_id", ""),
                    row.get("description", ""),
                    row.get("status", ""),
                    row.get("author", ""),
                    row.get("comment", ""),
                    row.get("date", ""),
                ]
            )

        # Create response with CSV file
        output = si.getvalue()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"work_order_comments_{timestamp}.csv"

        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        logger.error("Error exporting work order comments: %s", str(e))
        return jsonify({"success": False, "error": str(e)}), 500
