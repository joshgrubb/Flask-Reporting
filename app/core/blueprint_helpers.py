# app/core/blueprint_helpers.py
"""
Blueprint helper functions.

This module provides helpers for blueprint registration and management.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def create_report_blueprint(
    name,
    import_name,
    url_prefix,
    template_folder,
    report_name=None,
    description=None,
    group_id=None,
    icon=None,
):
    """
    Create a blueprint with report metadata.

    Args:
        name (str): Blueprint name
        import_name (str): Import name (__name__)
        url_prefix (str): URL prefix for routes
        template_folder (str): Template folder path
        report_name (str, optional): Human-readable report name
        description (str, optional): Report description
        group_id (str, optional): Parent group ID
        icon (str, optional): Font Awesome icon class

    Returns:
        Blueprint: Configured Flask blueprint
    """
    from flask import Blueprint

    # Create the blueprint
    bp = Blueprint(
        name, import_name, url_prefix=url_prefix, template_folder=template_folder
    )

    # Add report metadata
    bp.report_metadata = {
        "id": name,
        "name": report_name or name.replace("_", " ").title(),
        "description": description,
        "url": url_prefix,
        "group_id": group_id,
        "icon": icon,
    }

    logger.info("Created report blueprint: %s in group %s", name, group_id)
    return bp
