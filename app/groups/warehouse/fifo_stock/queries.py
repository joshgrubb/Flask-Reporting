"""
FIFO Stock Cost SQL Queries.

This module contains the SQL queries used in the FIFO Stock Cost report.
Each function returns a SQL query string and optional parameters.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def get_inventory_categories():
    """
    Get a list of all available inventory categories.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    query = """
    SELECT DISTINCT
        CATEGORY 
    FROM 
        [CW].[azteca].[MATERIALLEAF]
    WHERE 
        CATEGORY IS NOT NULL
    ORDER BY 
        CATEGORY
    """

    logger.info("Executing query to get inventory categories")
    return query, (), "cw"


def get_inventory_by_category(category):
    """
    Get inventory items by category.

    Args:
        category (str): The category to filter by.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Check if category is provided
    if not category:
        logger.warning("Category parameter is empty")
        # Return a query that will return no results
        return "SELECT 1 WHERE 1=0", ()

    # Build the query as provided in the requirements
    query = """
    SELECT 
        ML.MATERIALUID,
        ML.[DESCRIPTION],
        LF.QUANTITY,
        LF.UNITCOST,
        ML.CATEGORY,
        LF.PURCHASEDATE
    FROM 
        CW.azteca.LIFOFIFO LF
    INNER JOIN 
        CW.azteca.MATERIALLEAF ML
        ON ML.MATERIALSID = LF.MATERIALSID
    WHERE 
        LF.QUANTITY > 0
        AND ML.CATEGORY = ?
    ORDER BY 
        ML.CATEGORY,
        ML.MATERIALUID,
        LF.PURCHASEDATE
    """

    logger.info(f"Generated inventory query for category: {category}")
    return query, (category,), "cw"


def get_inventory_summary_by_category(category):
    """
    Get summary of inventory items by category.

    Args:
        category (str): The category to filter by.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Check if category is provided
    if not category:
        logger.warning("Category parameter is empty")
        # Return a query that will return no results
        return "SELECT 1 WHERE 1=0", ()

    # Build a summary query that aggregates by material ID
    query = """
    SELECT 
        ML.MATERIALUID,
        ML.[DESCRIPTION],
        SUM(LF.QUANTITY) AS TotalQuantity,
        AVG(LF.UNITCOST) AS AvgUnitCost,
        SUM(LF.QUANTITY * LF.UNITCOST) AS TotalValue,
        ML.CATEGORY,
        MIN(LF.PURCHASEDATE) AS OldestPurchaseDate,
        MAX(LF.PURCHASEDATE) AS NewestPurchaseDate
    FROM 
        CW.azteca.LIFOFIFO LF
    INNER JOIN 
        CW.azteca.MATERIALLEAF ML
        ON ML.MATERIALSID = LF.MATERIALSID
    WHERE 
        LF.QUANTITY > 0
        AND ML.CATEGORY = ?
    GROUP BY
        ML.MATERIALUID,
        ML.[DESCRIPTION],
        ML.CATEGORY
    ORDER BY 
        TotalValue DESC
    """

    logger.info(f"Generated inventory summary query for category: {category}")
    return query, (category,), "cw"
