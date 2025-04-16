# app/groups/public_works/fleet_costs/queries.py
"""
Fleet Costs SQL Queries.

This module contains the SQL queries used in the Fleet Costs report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)


def get_default_date_range():
    """
    Get the default date range for the report (last 90 days).

    Returns:
        tuple: A tuple containing (start_date, end_date) as datetime objects.
    """
    end_date = datetime.now().replace(hour=23, minute=59, second=59)
    start_date = (end_date - timedelta(days=90)).replace(hour=0, minute=0, second=0)

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


def get_fleet_costs(start_date=None, end_date=None, department=None):
    """
    Get fleet costs data for the specified date range and department.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 90 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.
        department (str, optional): Filter by specific department.
            If None, returns data for all departments.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Initialize parameters list
    params = [start_date_str, end_date_str]

    # Build the base query
    query = """
    SELECT WO.[WORKORDERID],
        WO.[ACTUALFINISHDATE],
        WO.[WOCATEGORY],
        WO.[WOLABORCOST],
        WO.[WOMATCOST],
        WO.[ACCTNUM],
        WO.[STATUS],
        WO.[WORKORDERSID],
        WOE.[ENTITYUID],
        MF.[Model],
        MF.[Department]
    FROM [CW].[azteca].[WORKORDER] WO
    LEFT JOIN [CW].[azteca].[WORKORDERENTITY] WOE
        ON WOE.[WORKORDERID] = WO.[WORKORDERID]
    LEFT JOIN [TOC_SDE].[GISMGR].[MOTOR_FLEET] MF
        ON MF.[EUID] = WOE.[ENTITYUID]
    WHERE WO.[WOCATEGORY] = 'MF'
        AND WO.[ACTUALFINISHDATE] BETWEEN ? AND ?
    """

    # Add department filter if provided
    if department:
        query += " AND MF.[Department] = ?"
        params.append(department)

    # Add ordering
    query += " ORDER BY WO.[ACTUALFINISHDATE] DESC"

    logger.info(
        "Generated fleet costs query for period %s to %s%s",
        start_date_str,
        end_date_str,
        f" for department {department}" if department else "",
    )

    return query, tuple(params), "cw"


def get_departments():
    """
    Get a list of all departments with fleet vehicles.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT DISTINCT [Department] 
    FROM [TOC_SDE].[GISMGR].[MOTOR_FLEET]
    WHERE [Department] IS NOT NULL
    ORDER BY [Department]
    """

    logger.info("Retrieving list of departments with fleet vehicles")
    return query, (), "cw"


def get_cost_summary_by_department(start_date=None, end_date=None):
    """
    Get cost summary grouped by department.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 90 days ago.
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
        MF.[Department],
        COUNT(DISTINCT WO.[WORKORDERID]) AS WorkOrderCount,
        SUM(WO.[WOLABORCOST]) AS TotalLaborCost,
        SUM(WO.[WOMATCOST]) AS TotalMaterialCost,
        SUM(WO.[WOLABORCOST] + WO.[WOMATCOST]) AS TotalCost
    FROM [CW].[azteca].[WORKORDER] WO
    LEFT JOIN [CW].[azteca].[WORKORDERENTITY] WOE
        ON WOE.[WORKORDERID] = WO.[WORKORDERID]
    LEFT JOIN [TOC_SDE].[GISMGR].[MOTOR_FLEET] MF
        ON MF.[EUID] = WOE.[ENTITYUID]
    WHERE WO.[WOCATEGORY] = 'MF'
        AND WO.[ACTUALFINISHDATE] BETWEEN ? AND ?
        AND MF.[Department] IS NOT NULL
    GROUP BY MF.[Department]
    ORDER BY TotalCost DESC
    """

    logger.info(
        "Generated department cost summary query for period %s to %s",
        start_date_str,
        end_date_str,
    )
    return query, tuple(params), "cw"


def get_cost_summary_by_vehicle(start_date=None, end_date=None, department=None):
    """
    Get cost summary grouped by vehicle.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 90 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.
        department (str, optional): Filter by specific department.
            If None, returns data for all departments.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Initialize parameters list
    params = [start_date_str, end_date_str]

    # Build the base query
    query = """
    SELECT 
        WOE.[ENTITYUID] AS VehicleID,
        MF.[Model] AS VehicleModel,
        MF.[Department],
        COUNT(DISTINCT WO.[WORKORDERID]) AS WorkOrderCount,
        SUM(WO.[WOLABORCOST]) AS TotalLaborCost,
        SUM(WO.[WOMATCOST]) AS TotalMaterialCost,
        SUM(WO.[WOLABORCOST] + WO.[WOMATCOST]) AS TotalCost
    FROM [CW].[azteca].[WORKORDER] WO
    LEFT JOIN [CW].[azteca].[WORKORDERENTITY] WOE
        ON WOE.[WORKORDERID] = WO.[WORKORDERID]
    LEFT JOIN [TOC_SDE].[GISMGR].[MOTOR_FLEET] MF
        ON MF.[EUID] = WOE.[ENTITYUID]
    WHERE WO.[WOCATEGORY] = 'MF'
        AND WO.[ACTUALFINISHDATE] BETWEEN ? AND ?
        AND WOE.[ENTITYUID] IS NOT NULL
    """

    # Add department filter if provided
    if department:
        query += " AND MF.[Department] = ?"
        params.append(department)

    # Complete the query with GROUP BY and ORDER BY
    query += """
    GROUP BY WOE.[ENTITYUID], MF.[Model], MF.[Department]
    ORDER BY TotalCost DESC
    """

    logger.info(
        "Generated vehicle cost summary query for period %s to %s%s",
        start_date_str,
        end_date_str,
        f" for department {department}" if department else "",
    )
    return query, tuple(params), "cw"


def get_costs_over_time(
    start_date=None, end_date=None, department=None, interval="month"
):
    """
    Get fleet costs aggregated over time periods.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 90 days ago.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to current date.
        department (str, optional): Filter by specific department.
            If None, returns data for all departments.
        interval (str, optional): Time interval for aggregation.
            Options: 'day', 'week', 'month', 'quarter', 'year'.
            Defaults to 'month'.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # For time-based analysis, make sure to include the entire period
    if interval == "year":
        # Fix: Make sure we include the entire date range, including the current year
        start_date = start_date.replace(month=1, day=1, hour=0, minute=0, second=0)
        # Ensure we keep the day intact to include the current (partial) year
        end_date = end_date.replace(hour=23, minute=59, second=59)
    elif interval == "month":
        # Extend to beginning of start month
        start_date = start_date.replace(day=1, hour=0, minute=0, second=0)
        # Keep the original end date but set to end of day
        end_date = end_date.replace(hour=23, minute=59, second=59)
    elif interval == "quarter":
        # Extend to beginning of start quarter
        start_quarter_month = ((start_date.month - 1) // 3) * 3 + 1
        start_date = start_date.replace(
            month=start_quarter_month, day=1, hour=0, minute=0, second=0
        )
        # Keep the original end date but set to end of day
        end_date = end_date.replace(hour=23, minute=59, second=59)

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Initialize parameters list
    params = [start_date_str, end_date_str]

    # Determine date grouping based on interval
    date_group_expr = ""
    if interval == "day":
        date_group_expr = "CONVERT(DATE, WO.[ACTUALFINISHDATE])"
    elif interval == "week":
        date_group_expr = "DATEADD(DAY, -DATEPART(WEEKDAY, WO.[ACTUALFINISHDATE]) + 1, CONVERT(DATE, WO.[ACTUALFINISHDATE]))"
    elif interval == "month":
        date_group_expr = "DATEFROMPARTS(YEAR(WO.[ACTUALFINISHDATE]), MONTH(WO.[ACTUALFINISHDATE]), 1)"
    elif interval == "quarter":
        date_group_expr = "DATEFROMPARTS(YEAR(WO.[ACTUALFINISHDATE]), ((DATEPART(QUARTER, WO.[ACTUALFINISHDATE]) - 1) * 3) + 1, 1)"
    elif interval == "year":
        date_group_expr = "DATEFROMPARTS(YEAR(WO.[ACTUALFINISHDATE]), 1, 1)"
    else:
        # Default to monthly if invalid interval provided
        date_group_expr = "DATEFROMPARTS(YEAR(WO.[ACTUALFINISHDATE]), MONTH(WO.[ACTUALFINISHDATE]), 1)"

    # Build the base query
    query = f"""
    SELECT 
        {date_group_expr} AS TimePeriod,
        COUNT(DISTINCT WO.[WORKORDERID]) AS WorkOrderCount,
        SUM(WO.[WOLABORCOST]) AS TotalLaborCost,
        SUM(WO.[WOMATCOST]) AS TotalMaterialCost,
        SUM(WO.[WOLABORCOST] + WO.[WOMATCOST]) AS TotalCost
    FROM [CW].[azteca].[WORKORDER] WO
    LEFT JOIN [CW].[azteca].[WORKORDERENTITY] WOE
        ON WOE.[WORKORDERID] = WO.[WORKORDERID]
    LEFT JOIN [TOC_SDE].[GISMGR].[MOTOR_FLEET] MF
        ON MF.[EUID] = WOE.[ENTITYUID]
    WHERE WO.[WOCATEGORY] = 'MF'
        AND WO.[ACTUALFINISHDATE] BETWEEN ? AND ?
    """

    # Add department filter if provided
    if department:
        query += " AND MF.[Department] = ?"
        params.append(department)

    # Complete the query with GROUP BY and ORDER BY
    query += f"""
    GROUP BY {date_group_expr}
    ORDER BY {date_group_expr}
    """

    logger.info(
        "Generated time-based cost query for period %s to %s, interval %s%s",
        start_date_str,
        end_date_str,
        interval,
        f", department {department}" if department else "",
    )
    return query, tuple(params), "cw"
