"""
Sewer Clean Length SQL Queries.

This module contains the SQL queries used in the Sewer Clean Length report.
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


def get_sewer_clean_data(start_date=None, end_date=None):
    """
    Get sewer clean data for the specified date range.

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

    # Build the query based on the provided template
    query = """
    SELECT
        wo.workorderid,
        wo.description,
        wo.actualfinishdate,
        we.entityuid,
        gm.objectid,
        gm.Shape.STLength() AS length
    FROM cw.azteca.workorder AS wo
    INNER JOIN cw.azteca.workorderentity AS we
        ON wo.workorderid = we.workorderid
    INNER JOIN toc_sde.gismgr.ssgravitymain AS gm
        ON we.entityuid = gm.euid
    WHERE
        wo.actualfinishdate >= ?
        AND wo.actualfinishdate <= ?
        AND wo.description IN (
            'Clean - Sewer Gravity Line',
            'Clean Trouble Spots - Sewer Gravity Line'
        )
    ORDER BY wo.actualfinishdate DESC;
    """

    logger.info(
        "Generated sewer clean data query for period %s to %s",
        start_date_str,
        end_date_str,
    )

    return query, tuple(params), "cw"  # "cw" is the database key for CityWorks


def get_daily_totals(start_date=None, end_date=None):
    """
    Get daily aggregated cleaning totals.

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

    # Build the query for daily aggregation
    query = """
    SELECT
        CONVERT(date, wo.actualfinishdate) AS clean_date,
        COUNT(DISTINCT wo.workorderid) AS work_order_count,
        SUM(gm.Shape.STLength()) AS total_length
    FROM cw.azteca.workorder AS wo
    INNER JOIN cw.azteca.workorderentity AS we
        ON wo.workorderid = we.workorderid
    INNER JOIN toc_sde.gismgr.ssgravitymain AS gm
        ON we.entityuid = gm.euid
    WHERE
        wo.actualfinishdate >= ?
        AND wo.actualfinishdate <= ?
        AND wo.description IN (
            'Clean - Sewer Gravity Line',
            'Clean Trouble Spots - Sewer Gravity Line'
        )
    GROUP BY CONVERT(date, wo.actualfinishdate)
    ORDER BY clean_date DESC;
    """

    logger.info(
        "Generated sewer clean daily totals query for period %s to %s",
        start_date_str,
        end_date_str,
    )

    return query, tuple(params), "cw"


def get_description_totals(start_date=None, end_date=None):
    """
    Get work type aggregated cleaning totals.

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

    # Build the query for description aggregation
    query = """
    SELECT
        wo.description AS work_type,
        COUNT(DISTINCT wo.workorderid) AS work_order_count,
        SUM(gm.Shape.STLength()) AS total_length
    FROM cw.azteca.workorder AS wo
    INNER JOIN cw.azteca.workorderentity AS we
        ON wo.workorderid = we.workorderid
    INNER JOIN toc_sde.gismgr.ssgravitymain AS gm
        ON we.entityuid = gm.euid
    WHERE
        wo.actualfinishdate >= ?
        AND wo.actualfinishdate <= ?
        AND wo.description IN (
            'Clean - Sewer Gravity Line',
            'Clean Trouble Spots - Sewer Gravity Line'
        )
    GROUP BY wo.description
    ORDER BY total_length DESC;
    """

    logger.info(
        "Generated sewer clean work type totals query for period %s to %s",
        start_date_str,
        end_date_str,
    )

    return query, tuple(params), "cw"
