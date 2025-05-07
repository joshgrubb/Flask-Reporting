# app/core/report_registry.py
"""
Report Registry Module.

This module provides a centralized registry for all application reports.
It serves as a single source of truth for dashboards, navigation, and search.
"""

import logging
from collections import defaultdict

# Configure logger
logger = logging.getLogger(__name__)

# Global registry to store all reports
_groups_registry = {}
_reports_registry = defaultdict(list)


def register_group(group_id, name, url, description=None, icon=None, enabled=True):
    """
    Register a report group in the registry.

    Args:
        group_id (str): Unique identifier for the group
        name (str): Display name for the group
        url (str): URL path to the group dashboard
        description (str, optional): Brief description of the group
        icon (str, optional): Font Awesome icon class for the group
        enabled (bool, optional): Whether the group is enabled

    Returns:
        dict: The registered group data
    """
    group_data = {
        "id": group_id,
        "name": name,
        "url": url,
        "description": description or f"{name} Reports",
        "icon": icon or "fas fa-folder",
        "enabled": enabled,
        "reports": [],  # Will be populated automatically when reports are registered
    }

    _groups_registry[group_id] = group_data
    logger.info("Registered report group: %s", group_id)
    return group_data


def register_report(
    report_id, name, url, group_id, description=None, icon=None, enabled=True
):
    """
    Register a report in the registry.

    Args:
        report_id (str): Unique identifier for the report
        name (str): Display name for the report
        url (str): URL path to access the report
        group_id (str): Parent group ID
        description (str, optional): Brief description of the report
        icon (str, optional): Font Awesome icon class for the report
        enabled (bool, optional): Whether the report is enabled

    Returns:
        dict: The registered report data
    """
    # Create group if it doesn't exist
    if group_id not in _groups_registry:
        logger.warning(
            "Group %s not found for report %s, creating placeholder",
            group_id,
            report_id,
        )
        register_group(
            group_id=group_id,
            name=group_id.replace("_", " ").title(),
            url=f"/groups/{group_id}/",
        )

    report_data = {
        "id": report_id,
        "name": name,
        "url": url,
        "description": description or f"{name} Report",
        "group_id": group_id,
        "icon": icon or "fas fa-file-alt",
        "enabled": enabled,
    }

    # Add to reports registry
    _reports_registry[group_id].append(report_data)

    # Also add to the group's reports list for easy access
    _groups_registry[group_id]["reports"].append(report_data)

    logger.info("Registered report: %s in group %s", report_id, group_id)
    return report_data


def get_all_groups():
    """
    Get all registered report groups.

    Returns:
        list: List of all group data dictionaries
    """
    return list(_groups_registry.values())


def get_group(group_id):
    """
    Get a specific report group by ID.

    Args:
        group_id (str): The group ID to retrieve

    Returns:
        dict: The group data or None if not found
    """
    return _groups_registry.get(group_id)


def get_all_reports():
    """
    Get all registered reports across all groups.

    Returns:
        list: List of all report data dictionaries
    """
    all_reports = []
    for reports in _reports_registry.values():
        all_reports.extend(reports)
    return all_reports


def get_group_reports(group_id):
    """
    Get all reports for a specific group.

    Args:
        group_id (str): The group ID to get reports for

    Returns:
        list: List of report data dictionaries for the group
    """
    return _reports_registry.get(group_id, [])


def extract_report_metadata(blueprint):
    """
    Extract report metadata from a blueprint.

    Args:
        blueprint: Flask Blueprint object with optional report_metadata

    Returns:
        dict: Extracted metadata or None if not available
    """
    if hasattr(blueprint, "report_metadata"):
        return blueprint.report_metadata

    # Try to infer from blueprint name and URL prefix
    if hasattr(blueprint, "name") and hasattr(blueprint, "url_prefix"):
        # Extract group_id from blueprint name (assuming pattern like 'group_name.report_name')
        name_parts = blueprint.name.split(".")
        if len(name_parts) >= 2:
            group_id = name_parts[0]
            report_id = name_parts[-1]

            return {
                "id": report_id,
                "name": report_id.replace("_", " ").title(),
                "url": blueprint.url_prefix,
                "group_id": group_id,
            }

    return None


def discover_reports_from_blueprints(app):
    """
    Discover and register reports from application blueprints.

    This function examines all registered blueprints in the Flask app
    and extracts report metadata when available.

    Args:
        app: Flask application instance
    """
    for blueprint_name, blueprint in app.blueprints.items():
        metadata = extract_report_metadata(blueprint)

        if metadata:
            try:
                # Get necessary fields with defaults
                report_id = metadata.get("id", blueprint_name.split(".")[-1])
                name = metadata.get("name", report_id.replace("_", " ").title())
                url = metadata.get("url") or blueprint.url_prefix or f"/{report_id}/"
                group_id = metadata.get("group_id")

                if group_id:  # Only register if we have a group_id
                    register_report(
                        report_id=report_id,
                        name=name,
                        url=url,
                        group_id=group_id,
                        description=metadata.get("description"),
                        icon=metadata.get("icon"),
                        enabled=metadata.get("enabled", True),
                    )
                    logger.info(
                        "Auto-discovered report: %s in group %s", report_id, group_id
                    )
            except Exception as e:
                logger.error(
                    "Failed to register report from blueprint %s: %s",
                    blueprint_name,
                    str(e),
                )


def initialize_report_registry(app):
    """
    Initialize the report registry with predefined groups and reports.

    This function should be called early in the application startup
    process, after blueprints are registered but before the first request.

    Args:
        app: Flask application instance
    """
    # Register groups first (from your existing navigation structure)
    register_group(
        group_id="utilities_billing",
        name="Utilities Billing",
        url="/groups/utilities_billing/",
        description="Reports related to utility billing, accounts, and services",
        icon="fas fa-file-invoice-dollar",
    )

    register_group(
        group_id="warehouse",
        name="Warehouse",
        url="/groups/warehouse/",
        description="Reports related to inventory, work orders, and stock management",
        icon="fas fa-warehouse",
    )

    register_group(
        group_id="finance",
        name="Finance",
        url="/groups/finance/",
        description="Financial reports and budget analysis",
        icon="fas fa-chart-pie",
    )

    register_group(
        group_id="public_works",
        name="Public Works",
        url="/groups/public_works/",
        description="Public Works reports on vehicles and solid waste",
        icon="fas fa-car",
    )

    register_group(
        group_id="community_development",
        name="Community Dev",
        url="/groups/community_development/",
        description="Reports for Engineering, Development Services, Inspections and Planning",
        icon="fas fa-file-circle-check",
    )

    register_group(
        group_id="water_resources",
        name="Water Resources",
        url="/groups/water_resources/",
        description="Reports related to water resources",
        icon="fas fa-water",
    )

    # Now discover reports from blueprints
    discover_reports_from_blueprints(app)

    # Make registry available to templates
    @app.context_processor
    def inject_report_registry():
        return {
            "report_registry": {
                "groups": get_all_groups(),
                "all_reports": get_all_reports(),
            },
            "get_all_groups": get_all_groups,
            "get_all_reports": get_all_reports,
            "get_group_reports": get_group_reports,
        }

    # Add an API endpoint for search functionality
    @app.route("/api/reports", methods=["GET"])
    def api_reports():
        """API endpoint to provide report data for search functionality."""
        return {"reports": get_all_reports()}

    logger.info(
        "Report registry initialized with %d groups and %d reports",
        len(_groups_registry),
        len(get_all_reports()),
    )
