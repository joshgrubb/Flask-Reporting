"""
Navigation helper module.

This module provides functionality for generating navigation data
for the application templates.
"""

import logging
from flask import current_app

# Configure logger
logger = logging.getLogger(__name__)


def get_navigation_data():
    """
    Generate navigation data for the application.

    This function returns structured data for the navbar
    containing groups and their associated reports.

    Returns:
        list: A list of dictionaries containing navigation data.
    """
    try:
        # Define navigation structure
        # This could potentially be loaded from a database or configuration file
        nav_groups = [
            {
                "id": "utilities_billing",
                "name": "Utilities Billing",
                "description": "Reports related to utility billing, accounts, and services",
                "url": "/groups/utilities_billing/",
                "icon": "fas fa-file-invoice-dollar",
                "reports": [
                    {
                        "name": "New Customer Accounts",
                        "url": "/groups/utilities_billing/new_customer_accounts/",
                    },
                    {
                        "name": "Amount Billed Search",
                        "url": "/groups/utilities_billing/amount_billed_search/",
                    },
                    {
                        "name": "Credit Balance",
                        "url": "/groups/utilities_billing/credit_balance/",
                    },
                    {
                        "name": "High Balance",
                        "url": "/groups/utilities_billing/high_balance/",
                    },
                    {
                        "name": "No Occupant for Moveouts",
                        "url": "/groups/utilities_billing/no_occupant_list_for_moveouts/",
                    },
                    {
                        "name": "Cash Only Accounts",
                        "url": "/groups/utilities_billing/cash_only_accounts/",
                    },
                    {
                        "name": "Accounts No Garbage",
                        "url": "/groups/utilities_billing/accounts_no_garbage/",
                    },
                ],
            },
            {
                "id": "warehouse",
                "name": "Warehouse",
                "description": "Reports related to inventory, work orders, and stock management",
                "url": "/groups/warehouse/",
                "icon": "fas fa-warehouse",
                "reports": [
                    {
                        "name": "FIFO Cost by Account",
                        "url": "/groups/warehouse/fifo_cost_wo/",
                    },
                    {
                        "name": "Inventory Cost Trends",
                        "url": "/groups/warehouse/fifo_stock/",
                    },
                    {
                        "name": "Audit Transactions",
                        "url": "/groups/warehouse/audit_transactions/",
                    },
                    {
                        "name": "Stock By Storeroom",
                        "url": "/groups/warehouse/stock_by_storeroom/",
                    },
                ],
            },
            {
                "id": "finance",
                "name": "Finance",
                "description": "Financial reports and budget analysis",
                "url": "/groups/finance/",
                "icon": "fas fa-chart-pie",
                "reports": [
                    {"name": "Budget Dashboard", "url": "/groups/finance/budget/"},
                    {
                        "name": "ClearGov Visualizations",
                        "url": "/groups/finance/cleargov/",
                    },
                ],
            },
            {
                "id": "public_works",
                "name": "Public Works",
                "description": "Public Works reports on vehicles and solid waste",
                "url": "/groups/public_works/",
                "icon": "fas fa-car",
                "reports": [
                    {"name": "Solid Waste", "url": "/groups/public_works/solid_waste/"},
                    {
                        "name": "Vehicle Fleet",
                        "url": "/groups/public_works/vehicle_fleet/",
                    },
                    {"name": "Fleet Costs", "url": "/groups/public_works/fleet_costs/"},
                ],
            },
            {
                "id": "community_development",
                "name": "Community Dev",
                "description": "Reports for Engineering, Development Services, Inspections and Planning",
                "url": "/groups/community_development/",
                "icon": "fas fa-file-circle-check",
                "reports": [
                    {
                        "name": "Bluebeam",
                        "url": "/groups/community_development/bluebeam/",
                    },
                    {
                        "name": "Permits & Inspections",
                        "url": "/groups/community_development/permits_inspections/",
                    },
                ],
            },
            {
                "id": "water_resources",
                "name": "Water Resources",
                "description": "Reports related to water resources",
                "url": "/groups/water_resources/",
                "icon": "fas fa-water",
                "reports": [
                    {
                        "name": "Hydrant History",
                        "url": "/groups/water_resources/hydrant_history/",
                    },
                ],
            },
        ]

        logger.info("Generated navigation data with %d groups", len(nav_groups))
        return nav_groups

    except Exception as e:
        logger.error("Error generating navigation data: %s", str(e))
        # Return empty list in case of error
        return []
