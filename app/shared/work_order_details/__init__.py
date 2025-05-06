# app/shared/work_order_details/__init__.py
"""
Work Order Details Module.

This module provides a shareable report for viewing work order details
that can be accessed from multiple group blueprints.
"""

# Import the route registration function so it can be imported directly
# from this module
from app.shared.work_order_details.routes import register_work_order_details_routes

# Export the route registration function
__all__ = ["register_work_order_details_routes"]
