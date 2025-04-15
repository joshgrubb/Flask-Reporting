"""
Work Order Counts SQL Queries.

This module contains the SQL queries used in the Work Order Counts report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)


def get_default_date_range():
    """
    Get the default date range for the report (last 30 days).

    Returns:
        tuple: A tuple containing (start_date, end_date) as datetime objects.
    """
    end_date = datetime.now().replace(hour=23, minute=59, second=59)
    start_date = (end_date - timedelta(days=30)).replace(hour=0, minute=0, second=0)

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


def get_work_order_counts_by_user(start_date=None, end_date=None):
    """
    Get work order counts grouped by user.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Parameters
    params = [start_date_str, end_date_str]

    # Build the query
    query = """
    SELECT su.UserName,
        COUNT(*) AS CountUser
    FROM [LogosDB].[dbo].[WorkOrders] AS wo
    INNER JOIN [LogosDB].[dbo].[SecurityUser] AS su
        ON su.UserID = wo.RequestedByEmployeeID
    WHERE wo.CreateDate BETWEEN ?
            AND ?
    GROUP BY su.UserName
    ORDER BY CountUser DESC
    """

    logger.info(
        "Generated work order counts query for period %s to %s",
        start_date_str,
        end_date_str,
    )
    return query, tuple(params), "nws"


def get_work_orders_daily_counts(start_date=None, end_date=None):
    """
    Get daily counts of work orders.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Parameters
    params = [start_date_str, end_date_str]

    # Build the query
    query = """
    SELECT 
        CONVERT(date, wo.CreateDate) AS CreateDate,
        COUNT(*) AS DailyCount
    FROM [LogosDB].[dbo].[WorkOrders] AS wo
    WHERE wo.CreateDate BETWEEN ?
            AND ?
    GROUP BY CONVERT(date, wo.CreateDate)
    ORDER BY CONVERT(date, wo.CreateDate)
    """

    logger.info(
        "Generated daily work order counts query for period %s to %s",
        start_date_str,
        end_date_str,
    )
    return query, tuple(params), "nws"


def get_work_orders_by_type(start_date=None, end_date=None):
    """
    Get work order counts grouped by type.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Parameters
    params = [start_date_str, end_date_str]

    # Build the query
    query = """
    SELECT ISNULL(LTRIM(wot.WorkOrderCode), 'Unknown') AS TypeName,
        COUNT(*) AS TypeCount
    FROM [LogosDB].[dbo].[WorkOrders] AS wo
    LEFT JOIN [LogosDB].[dbo].[WorkOrderType] AS wot
        ON wo.WorkOrderTypeID = wot.WorkOrderTypeID
    WHERE wo.CreateDate BETWEEN ?
            AND ?
    GROUP BY LTRIM(wot.WorkOrderCode)
    ORDER BY TypeCount DESC;

    """

    logger.info(
        "Generated work order type counts query for period %s to %s",
        start_date_str,
        end_date_str,
    )
    return query, tuple(params), "nws"
