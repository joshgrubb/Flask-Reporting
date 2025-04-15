# app/groups/water_resources/hydrant_history/queries.py
"""
Hydrant History SQL Queries.

This module contains the SQL queries used in the Hydrant History report.
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


def get_hydrant_inspections(start_date=None, end_date=None, hydrant_id=None):
    """
    Get hydrant inspection data for the specified date range.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.
        hydrant_id (str, optional): Filter by specific hydrant ID.

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

    # Build the base query
    query = """
    SELECT [INSPECTIONID],
        [WORKORDERID],
        [INSPTEMPLATENAME],
        [ENTITYUID],
        [ENTITYTYPE],
        [INSPDATE],
        [STATUS]
    FROM [CW].[azteca].[INSPECTION]
    WHERE [INSPTEMPLATENAME] = 'Fire Hydrant Inspection'
        OR [INSPTEMPLATENAME] = 'Hydrant Flow Test'
        AND [INSPDATE] BETWEEN ? AND ?
    """

    # Add hydrant ID filter if provided
    if hydrant_id:
        query += " AND [ENTITYUID] = ?"
        params.append(hydrant_id)

    # Add ordering
    query += " ORDER BY [INSPDATE] DESC"

    logger.info(
        "Generated hydrant inspections query for period %s to %s%s",
        start_date_str,
        end_date_str,
        f" for hydrant {hydrant_id}" if hydrant_id else "",
    )

    return query, tuple(params), "cw"


def get_hydrant_work_orders(start_date=None, end_date=None, hydrant_id=None):
    """
    Get hydrant work order data for the specified date range.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.
        hydrant_id (str, optional): Filter by specific hydrant ID.

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
    SELECT [CW].[azteca].[WORKORDER].[WORKORDERID],
        [CW].[azteca].[WORKORDER].[DESCRIPTION],
        [CW].[azteca].[WORKORDER].[ACTUALFINISHDATE],
        [CW].[azteca].[WORKORDER].[STATUS],
        [CW].[azteca].[WORKORDERENTITY].[ENTITYUID]
    FROM [CW].[azteca].[WORKORDER]
    INNER JOIN [CW].[azteca].[WORKORDERENTITY]
        ON [CW].[azteca].[WORKORDERENTITY].[WORKORDERID] = [CW].[azteca].[WORKORDER].[WORKORDERID]
    WHERE [CW].[azteca].[WORKORDER].[APPLYTOENTITY] = 'WHYDRANTS'
        AND [CW].[azteca].[WORKORDER].[ACTUALFINISHDATE] BETWEEN ? AND ?
    """

    # Add hydrant ID filter if provided
    if hydrant_id:
        query += " AND [CW].[azteca].[WORKORDERENTITY].[ENTITYUID] = ?"
        params.append(hydrant_id)

    # Add ordering
    query += " ORDER BY CAST([CW].[azteca].[WORKORDERENTITY].[ENTITYUID] AS INT), [CW].[azteca].[WORKORDER].[ACTUALFINISHDATE] DESC"

    logger.info(
        "Generated hydrant work orders query for period %s to %s%s",
        start_date_str,
        end_date_str,
        f" for hydrant {hydrant_id}" if hydrant_id else "",
    )

    return query, tuple(params), "cw"
