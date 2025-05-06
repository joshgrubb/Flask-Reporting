# app/shared/work_order_comments/queries.py
"""
Work Order Comments Search SQL Queries.

This module contains the SQL queries for the Work Order Comments Search report.
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


def get_work_order_comments(search_term, start_date=None, end_date=None):
    """
    Get work order comments that match the search term within the date range.

    Args:
        search_term (str): The term to search for in comments.
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

    # Build the base query
    query = """
    SELECT
        WOC.WORKORDERID,
        WOC.AUTHORSID,
        E.EMPLOYEEID,
        E.LASTNAME,
        E.FIRSTNAME,
        WOC.COMMENTS,
        WOC.DATECREATED,
        WO.DESCRIPTION,
        WO.STATUS
    FROM CW.[azteca].WORKORDERCOMMENT AS WOC
    LEFT JOIN CW.[azteca].EMPLOYEE AS E
        ON WOC.AUTHORSID = E.EMPLOYEESID
    LEFT JOIN CW.[azteca].WORKORDER AS WO
        ON WOC.WORKORDERID = WO.WORKORDERID
    WHERE 
        WOC.COMMENTS LIKE ?
        AND WOC.DATECREATED BETWEEN ? AND ?
    ORDER BY WOC.DATECREATED DESC
    """

    # Parameters - using ? placeholder style for pyodbc
    # Add wildcards to the search term for partial matching
    params = [f"%{search_term}%", start_date_str, end_date_str]

    logger.info(
        "Generated work order comments search query for term '%s' between %s and %s",
        search_term,
        start_date_str,
        end_date_str,
    )

    return query, tuple(params), "cw"  # "cw" is the database key for CityWorks


def get_employee_list():
    """
    Get all employees for filter dropdown.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT 
        EMPLOYEEID, 
        EMPLOYEESID,
        FIRSTNAME,
        LASTNAME
    FROM CW.[azteca].EMPLOYEE
    WHERE LASTNAME IS NOT NULL
    ORDER BY LASTNAME, FIRSTNAME
    """

    logger.info("Retrieving employee list for filter dropdown")
    return query, (), "cw"  # Empty tuple for params
