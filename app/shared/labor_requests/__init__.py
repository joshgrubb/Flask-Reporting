"""
Labor Requests Module.

This module provides a shareable report for labor requests
that can be accessed from multiple group blueprints.
"""

from flask import Blueprint

# Create a test blueprint for direct access
test_bp = Blueprint(
    "labor_requests_test",
    __name__,
    url_prefix="/labor_requests_test",
    template_folder="../../templates/shared/labor_requests",
)

# Add report metadata even though this is a shared report
test_bp.report_metadata = {
    "id": "labor_requests",
    "name": "Labor Requests",
    "description": "View and analyze labor requests",
    "url": "/labor_requests_test/",
    "group_id": "shared",  # This will be overridden when registered with a group
    "icon": "fas fa-hard-hat",
}

# Import the route registration function so it can be imported directly
from app.shared.labor_requests.routes import register_labor_requests_routes

# Export the route registration function and test blueprint
__all__ = ["register_labor_requests_routes", "test_bp"]
