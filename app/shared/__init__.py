"""
Shared modules package.

This package contains shared report modules that can be accessed from multiple group blueprints.
"""

# Import shared modules for easier access
from app.shared.labor_requests import register_labor_requests_routes
from app.shared.work_order_comments import register_work_order_comments_routes
from app.shared.work_order_details import register_work_order_details_routes

# Export the registration functions
__all__ = [
    "register_labor_requests_routes",
    "register_work_order_comments_routes",
    "register_work_order_details_routes",
]
