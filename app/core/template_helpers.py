"""
Template Helper Functions.

This module provides helper functions that can be used in Jinja2 templates.
"""

import logging
from typing import List, Dict, Any, Optional

# Changed import to use Markup from Jinja2 instead of Flask
from markupsafe import Markup
from .cdn_config import CDNResourceManager

# Configure logger
logger = logging.getLogger(__name__)


def include_cdn_resources(
    resources: Optional[List[str]] = None, bundles: Optional[List[str]] = None
) -> Markup:
    """
    Generate HTML tags for including CDN resources.

    This function can include resources by individual ID or by bundle name.

    Args:
        resources: List of resource IDs to include.
        bundles: List of bundle names to include.

    Returns:
        Markup object containing HTML tags for the requested resources.
    """
    try:
        # List to store all resources
        all_resources = []

        # Add individual resources
        if resources:
            all_resources.extend(CDNResourceManager.get_resources_by_ids(resources))

        # Add bundle resources
        if bundles:
            all_resources.extend(CDNResourceManager.get_resources_for_bundles(bundles))

        # Remove duplicates while preserving order
        unique_resources = {}
        for resource in all_resources:
            unique_resources[resource["url"]] = resource

        # Group resources by type for better HTML structure
        css_resources = []
        js_resources = []

        for resource in unique_resources.values():
            if resource["type"] == CDNResourceManager.TYPE_CSS:
                css_resources.append(resource)
            elif resource["type"] == CDNResourceManager.TYPE_JS:
                js_resources.append(resource)

        # Generate HTML tags
        html = "\n".join(
            [CDNResourceManager.generate_resource_tag(res) for res in css_resources]
            + [CDNResourceManager.generate_resource_tag(res) for res in js_resources]
        )

        return Markup(html)

    except Exception as e:
        logger.error("Error including CDN resources: %s", str(e))
        return Markup(f"<!-- Error loading CDN resources: {str(e)} -->")


def register_template_helpers(app):
    """
    Register template helper functions with a Flask application.

    Args:
        app: The Flask application.
    """
    app.jinja_env.globals.update(
        include_cdn=include_cdn_resources, get_blueprint_group_id=get_blueprint_group_id
    )


def get_blueprint_group_id(blueprint):
    """
    Extract the group_id from a blueprint.

    This function handles different types of input to reliably extract
    the group ID. It works with Blueprint objects, strings, or None.

    Args:
        blueprint: Flask Blueprint object, string, or None

    Returns:
        str: The extracted group_id or None if it cannot be determined
    """
    if blueprint is None:
        logger.warning("Received None blueprint when trying to get group_id")
        return None

    # Handle string input (might be blueprint name or already a group_id)
    if isinstance(blueprint, str):
        # Check if it contains a dot (indicating blueprint.name format)
        if "." in blueprint:
            return blueprint.split(".")[0]
        return blueprint

    # Blueprint object with report_metadata
    if hasattr(blueprint, "report_metadata") and blueprint.report_metadata:
        if "group_id" in blueprint.report_metadata:
            return blueprint.report_metadata["group_id"]

    # Try to extract from blueprint name
    if hasattr(blueprint, "name"):
        # If name contains a dot, take the first part as group_id
        if "." in blueprint.name:
            return blueprint.name.split(".")[0]
        return blueprint.name

    # If we get here, log a warning and return None
    logger.warning("Could not determine group_id from blueprint: %s", blueprint)
    return None
