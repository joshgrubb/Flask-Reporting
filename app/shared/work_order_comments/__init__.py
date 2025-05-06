# app/shared/work_order_comments/__init__.py
"""
Work Order Comments Search Module.

This module provides a shareable report for searching work order comments
that can be accessed from multiple group blueprints.
"""

# Import the route registration function so it can be imported directly
# from this module
from app.shared.work_order_comments.routes import register_work_order_comments_routes

# Export the route registration function
__all__ = ["register_work_order_comments_routes"]
