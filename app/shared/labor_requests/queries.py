"""
Labor Requests SQL Queries.

This module contains the SQL queries for the Labor Requests report.
Each function returns a SQL query string and parameters.
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


def get_labor_requests(start_date=None, end_date=None, category=None):
    """
    Get labor request data for the specified date range and category.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.
        category (str, optional): Filter by specific request category.
            If None, returns all categories.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Build the base query
    query = """
    SELECT
        CW.[azteca].REQUESTLABOR.REQUESTID,
        CW.[azteca].REQUESTLABOR.LABORNAME,
        CW.[azteca].REQUESTLABOR.HOURS,
        CW.[azteca].REQUESTLABOR.COST,
        CW.[azteca].REQUESTLABOR.TRANSDATE,
        CW.[azteca].REQUEST.DESCRIPTION,
        CW.[azteca].REQUEST.REQCATEGORY
    FROM CW.[azteca].REQUESTLABOR
    INNER JOIN
        CW.[azteca].REQUEST
        ON CW.[azteca].REQUEST.REQUESTID = CW.[azteca].REQUESTLABOR.REQUESTID
    WHERE
        CW.[azteca].REQUESTLABOR.TRANSDATE BETWEEN ? AND ?
    """

    # Parameters - using ? placeholder style for pyodbc
    params = [start_date_str, end_date_str]

    # Add category filter if provided
    if category:
        query += " AND CW.[azteca].REQUEST.REQCATEGORY = ?"
        params.append(category)

    # Add ordering
    query += " ORDER BY CW.[azteca].REQUEST.DESCRIPTION"

    logger.info(
        "Generated labor requests query for period %s to %s%s",
        start_date_str,
        end_date_str,
        f" for category {category}" if category else "",
    )

    return query, tuple(params), "cw"  # "cw" is the database key for CityWorks database


def get_request_categories():
    """
    Get all unique request categories.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT DISTINCT REQCATEGORY
    FROM CW.[azteca].REQUEST
    WHERE REQCATEGORY IS NOT NULL
    ORDER BY REQCATEGORY
    """

    logger.info("Retrieving unique request categories")
    return query, (), "cw"  # Empty tuple for params, "cw" database key
