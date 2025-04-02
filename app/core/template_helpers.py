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
        logger.error(f"Error including CDN resources: {str(e)}")
        return Markup(f"<!-- Error loading CDN resources: {str(e)} -->")


def register_template_helpers(app):
    """
    Register template helper functions with a Flask application.

    Args:
        app: The Flask application.
    """
    app.jinja_env.globals.update(include_cdn=include_cdn_resources)
