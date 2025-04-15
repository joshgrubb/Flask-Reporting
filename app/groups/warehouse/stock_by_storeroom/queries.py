# app/groups/warehouse/stock_by_storeroom/queries.py
"""
Stock By Storeroom SQL Queries.

This module contains the SQL queries used in the Stock By Storeroom report.
Each function returns a SQL query string and optional parameters.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def get_storerooms():
    """
    Get a list of all available storerooms.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT DISTINCT STORERM
    FROM [CW].[azteca].[STORERMSTOCK]
    WHERE STORERM IS NOT NULL
    ORDER BY STORERM
    """

    logger.info("Executing query to get storeroom list")
    return query, (), "cw"


def get_stock_by_storeroom(storeroom):
    """
    Get inventory items for a specific storeroom.

    Args:
        storeroom (str): The storeroom code to filter by.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Check if storeroom is provided
    if not storeroom:
        logger.warning("Storeroom parameter is empty")
        # Return a query that will return no results
        return "SELECT 1 WHERE 1=0", (), "cw"

    # Build the query from the provided SQL
    query = """
    SELECT ml.MATERIALUID,
        ml.DESCRIPTION,
        st.STORERM,
        st.MINQUANTITY,
        st.STOCKONHAND,
        st.MAXQUANTITY,
        - (st.STOCKONHAND - st.MINQUANTITY) AS [Under_Min]
    FROM [CW].[azteca].[MATERIALLEAF] ml
    INNER JOIN [CW].[azteca].[STORERMSTOCK] st
        ON ml.MATERIALSID = st.MATERIALSID
    WHERE st.STORERM = ?
        AND ml.VIEWABLE = '1'
    ORDER BY ml.MATERIALUID
    """

    logger.info("Generated stock by storeroom query for storeroom: %s", storeroom)
    return query, (storeroom,), "cw"


def get_summary_by_storeroom(storeroom):
    """
    Get summary statistics for a specific storeroom.

    Args:
        storeroom (str): The storeroom code to filter by.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Check if storeroom is provided
    if not storeroom:
        logger.warning("Storeroom parameter is empty")
        # Return a query that will return no results
        return "SELECT 1 WHERE 1=0", (), "cw"

    # Build a summary query
    query = """
    SELECT 
        COUNT(ml.MATERIALUID) AS TotalItems,
        SUM(CASE WHEN st.STOCKONHAND < st.MINQUANTITY THEN 1 ELSE 0 END) AS UnderMinCount,
        SUM(CASE WHEN st.STOCKONHAND > st.MAXQUANTITY THEN 1 ELSE 0 END) AS OverMaxCount,
        SUM(CASE WHEN st.STOCKONHAND BETWEEN st.MINQUANTITY AND st.MAXQUANTITY THEN 1 ELSE 0 END) AS NormalCount,
        SUM(st.STOCKONHAND) AS TotalOnHand
    FROM [CW].[azteca].[MATERIALLEAF] ml
    INNER JOIN [CW].[azteca].[STORERMSTOCK] st
        ON ml.MATERIALSID = st.MATERIALSID
    WHERE st.STORERM = ?
        AND ml.VIEWABLE = '1'
    """

    logger.info("Generated storeroom summary query for storeroom: %s", storeroom)
    return query, (storeroom,), "cw"
