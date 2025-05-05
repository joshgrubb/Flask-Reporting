"""
Labor Requests Module.

This module provides a shareable report for labor requests
that can be accessed from multiple group blueprints.
"""

# Import the route registration function so it can be imported directly
# from this module
from app.shared.labor_requests.routes import register_labor_requests_routes

# Import the test blueprint for debugging purposes
from app.shared.labor_requests.test_route import test_bp

# Export the route registration function and test blueprint
__all__ = ["register_labor_requests_routes", "test_bp"]
