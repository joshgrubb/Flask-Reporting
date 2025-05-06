"""
Work Order Details Module.

This module provides a shareable report for viewing work order details
that can be accessed from multiple group blueprints.
"""


# Directly define the function here to avoid circular imports
def register_work_order_details_routes(bp, url_prefix="/work_orders"):
    """Import and register the routes with the given blueprint."""
    from app.shared.work_order_details.routes import setup_routes

    return setup_routes(bp, url_prefix)


# Export the registration function
__all__ = ["register_work_order_details_routes"]
