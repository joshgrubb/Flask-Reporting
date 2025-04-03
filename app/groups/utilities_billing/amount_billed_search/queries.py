"""
Amount Billed Search SQL Queries.

This module contains the SQL queries used in the Amount Billed Search report.
Each function returns a SQL query string and optional parameters.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def get_bill_amount_search(amount):
    """
    Get bill amount search results.

    Args:
        amount (str): The bill amount to search for, can include wildcards.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    if not amount:
        logger.warning("Empty amount parameter provided for bill search")
        # Return a query that will return no results
        return "SELECT 1 WHERE 1=0", ()

    # Prepare the search parameter
    search_amount = amount

    # Check if wildcards are already included
    if "%" not in search_amount:
        # Add wildcards for partial matching
        search_amount = f"%{search_amount}%"

    logger.info(f"Preparing bill amount search for: {search_amount}")

    # Build the query based on the original SSRS query
    query = """
    SELECT 
        BA.BillAmount, 
        UA.FullAccountNumber, 
        BA.AuditDate
    FROM 
        [LogosDB].[dbo].[UtilityBillAudit] AS BA
    INNER JOIN 
        [LogosDB].[dbo].[UtilityAccount] AS UA
        ON BA.UtilityAccountID = UA.UtilityAccountID
    WHERE 
        BA.BillAmount LIKE ?
    ORDER BY 
        BA.AuditDate DESC
    OPTION (RECOMPILE)
    """

    # Parameters
    params = (search_amount,)

    return query, params, "nws"
