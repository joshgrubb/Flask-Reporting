"""
FIFO Work Order Cost SQL Queries.

This module contains the SQL queries used in the FIFO Work Order Cost report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)


def get_default_date_range():
    """
    Get the default date range for the report (last complete calendar month).
    For example, if today is 4/3/2025, the range would be 3/1/2025 to 3/31/2025.

    Returns:
        tuple: A tuple containing (start_date, end_date) as datetime objects.
    """
    today = datetime.now()

    # Get the first day of the current month
    first_day_current_month = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    # Get the last day of the previous month by subtracting 1 day from the first day of current month
    end_date = first_day_current_month - timedelta(days=1)
    end_date = end_date.replace(hour=23, minute=59, second=59)

    # Get the first day of the previous month
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    return start_date, end_date


def format_date_for_query(date_obj):
    """
    Format a datetime object for SQL Server query.

    Args:
        date_obj (datetime): The datetime object to format.

    Returns:
        str: Formatted date string for SQL Server.
    """
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")


def get_fifo_work_order_costs(start_date=None, end_date=None):
    """
    Get work order costs data using FIFO inventory method.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Parameters
    params = [start_date_str, end_date_str]

    # Build the query using the provided SQL
    query = """
    SELECT MAT.ACCTNUM,
        MAT.COST,
        WO.WORKORDERID,
        MAT.MATERIALUID,
        MAT.UNITSREQUIRED,
        MAT.TRANSDATE,
        WO.WOCATEGORY,
        MAT.[DESCRIPTION]
    FROM [CW].[azteca].[WORKORDER] WO
    INNER JOIN azteca.MATERIALCOSTACT AS MAT
        ON WO.WORKORDERID = MAT.WORKORDERID
    WHERE MAT.TRANSDATE >= ?
        AND MAT.TRANSDATE <= ?
        AND MAT.MATERIALUID IS NOT NULL
        AND WO.WOCATEGORY IN ('ELEC', 'W-S-PS')
        AND (
            MAT.Source = 'WAREHOUSE'
            OR MAT.Source LIKE '%truck%'
            )
    ORDER BY MAT.TRANSDATE DESC, WO.WORKORDERID
    """

    logger.info(
        f"Generated FIFO work order costs query for period {start_date_str} to {end_date_str}"
    )
    return query, tuple(params), "cw"  # Note we're using "cw" database key


def get_work_order_summary(start_date=None, end_date=None):
    """
    Get summary of work order costs by category.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Parameters
    params = [start_date_str, end_date_str]

    # Build the query for summary data
    query = """
    SELECT 
        WO.WOCATEGORY AS Category,
        COUNT(DISTINCT WO.WORKORDERID) AS WorkOrderCount,
        SUM(MAT.COST) AS TotalCost
    FROM [CW].[azteca].[WORKORDER] WO
    INNER JOIN azteca.MATERIALCOSTACT AS MAT
        ON WO.WORKORDERID = MAT.WORKORDERID
    WHERE MAT.TRANSDATE >= ?
        AND MAT.TRANSDATE <= ?
        AND MAT.MATERIALUID IS NOT NULL
        AND WO.WOCATEGORY IN ('ELEC', 'W-S-PS')
        AND (
            MAT.Source = 'WAREHOUSE'
            OR MAT.Source LIKE '%truck%'
            )
    GROUP BY WO.WOCATEGORY
    ORDER BY WO.WOCATEGORY
    """

    logger.info(
        f"Generated work order summary query for period {start_date_str} to {end_date_str}"
    )
    return query, tuple(params), "cw"
