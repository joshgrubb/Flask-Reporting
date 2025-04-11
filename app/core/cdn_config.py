"""
CDN Resource Configuration Module.

This module provides a centralized management system for CDN resources
used across the application's templates.
"""

from typing import Dict, List, Any
import logging

# Configure logger
logger = logging.getLogger(__name__)


class CDNResourceManager:
    """
    Manages CDN resources for the application.

    This class provides methods to register and retrieve CDN resources,
    organize them into bundles, and generate the necessary HTML tags.
    """

    # Resource types
    TYPE_CSS = "css"
    TYPE_JS = "js"

    # Resource definitions with versioning
    RESOURCES = {
        # CSS Resources
        "bootstrap-css": {
            "type": TYPE_CSS,
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
        },
        "fontawesome-css": {
            "type": TYPE_CSS,
            "url": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css",
        },
        "datatables-css": {
            "type": TYPE_CSS,
            "url": "https://cdn.datatables.net/2.2.2/css/dataTables.bootstrap5.min.css",
        },
        "flatpickr-css": {
            "type": TYPE_CSS,
            "url": "https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css",
        },
        # JavaScript Resources
        "bootstrap-js": {
            "type": TYPE_JS,
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        },
        "jquery": {
            "type": TYPE_JS,
            "url": "https://code.jquery.com/jquery-3.7.1.min.js",
        },
        "chartjs": {
            "type": TYPE_JS,
            "url": "https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js",
        },
        "datatables-js": {
            "type": TYPE_JS,
            "url": "https://cdn.datatables.net/2.2.2/js/dataTables.min.js",
        },
        "datatables-bs5-js": {
            "type": TYPE_JS,
            "url": "https://cdn.datatables.net/2.2.2/js/dataTables.bootstrap5.min.js",
        },
        "flatpickr-js": {
            "type": TYPE_JS,
            "url": "https://cdn.jsdelivr.net/npm/flatpickr",
            "defer": True,
        },
        "bootstrap-multiselect-css": {
            "type": TYPE_CSS,
            "url": "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-multiselect/1.1.2/css/bootstrap-multiselect.min.css",
        },
        "bootstrap-multiselect-js": {
            "type": TYPE_JS,
            "url": "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-multiselect/1.1.2/js/bootstrap-multiselect.min.js",
        },
        "select2-css": {
            "type": TYPE_CSS,
            "url": "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css",
        },
        "select2-js": {
            "type": TYPE_JS,
            "url": "https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js",
        },
    }

    # Resource bundles for common use cases
    BUNDLES = {
        "core": ["bootstrap-css", "fontawesome-css", "bootstrap-js", "jquery"],
        "datatables": ["datatables-css", "datatables-js", "datatables-bs5-js"],
        "chartjs": ["chartjs"],
        "datepicker": ["flatpickr-css", "flatpickr-js"],
        "multiselect": ["bootstrap-multiselect-css", "bootstrap-multiselect-js"],
        "select2": ["select2-css", "select2-js"],
    }

    @classmethod
    def get_resource(cls, resource_id: str) -> Dict[str, Any]:
        """
        Get a resource by ID.

        Args:
            resource_id: The ID of the resource to retrieve.

        Returns:
            The resource configuration dictionary.

        Raises:
            KeyError: If the resource ID is not found.
        """
        if resource_id not in cls.RESOURCES:
            logger.warning(f"Resource not found: {resource_id}")
            raise KeyError(f"Resource not found: {resource_id}")

        return cls.RESOURCES[resource_id]

    @classmethod
    def get_bundle(cls, bundle_id: str) -> List[Dict[str, Any]]:
        """
        Get all resources in a bundle.

        Args:
            bundle_id: The ID of the bundle to retrieve.

        Returns:
            List of resource configuration dictionaries.

        Raises:
            KeyError: If the bundle ID is not found.
        """
        if bundle_id not in cls.BUNDLES:
            logger.warning(f"Bundle not found: {bundle_id}")
            raise KeyError(f"Bundle not found: {bundle_id}")

        resources = []
        for resource_id in cls.BUNDLES[bundle_id]:
            try:
                resources.append(cls.get_resource(resource_id))
            except KeyError:
                logger.error(f"Resource {resource_id} in bundle {bundle_id} not found")

        return resources

    @classmethod
    def get_resources_by_ids(cls, resource_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple resources by their IDs.

        Args:
            resource_ids: List of resource IDs to retrieve.

        Returns:
            List of resource configuration dictionaries.
        """
        resources = []
        for resource_id in resource_ids:
            try:
                resources.append(cls.get_resource(resource_id))
            except KeyError:
                logger.error(f"Resource {resource_id} not found")

        return resources

    @classmethod
    def get_resources_for_bundles(cls, bundle_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get all resources from multiple bundles, with duplicates removed.

        Args:
            bundle_ids: List of bundle IDs to retrieve.

        Returns:
            List of unique resource configuration dictionaries.
        """
        # Use a dict to remove duplicates while preserving order
        resource_map = {}

        for bundle_id in bundle_ids:
            try:
                for resource in cls.get_bundle(bundle_id):
                    # Use URL as a unique key
                    resource_map[resource["url"]] = resource
            except KeyError:
                logger.error(f"Bundle {bundle_id} not found")

        return list(resource_map.values())

    @staticmethod
    def generate_resource_tag(resource: Dict[str, Any]) -> str:
        """
        Generate HTML tag for a resource.

        Args:
            resource: Resource configuration dictionary.

        Returns:
            HTML tag for the resource.
        """
        if resource["type"] == CDNResourceManager.TYPE_CSS:
            tag = f'<link rel="stylesheet" href="{resource["url"]}"'

            if "integrity" in resource:
                tag += f' integrity="{resource["integrity"]}"'

            if "crossorigin" in resource:
                tag += f' crossorigin="{resource["crossorigin"]}"'

            tag += ">"
            return tag

        elif resource["type"] == CDNResourceManager.TYPE_JS:
            tag = f'<script src="{resource["url"]}"'

            if "integrity" in resource:
                tag += f' integrity="{resource["integrity"]}"'

            if "crossorigin" in resource:
                tag += f' crossorigin="{resource["crossorigin"]}"'

            if "defer" in resource and resource["defer"]:
                tag += " defer"

            tag += "></script>"
            return tag

        return ""  # Unknown resource type
