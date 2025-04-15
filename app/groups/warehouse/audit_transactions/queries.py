"""
Warehouse Audit Transactions SQL Queries.

This module contains the SQL queries used in the Warehouse Audit Transactions report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)


def get_default_date_range():
    """
    Get the default date range for the report (previous month).

    Returns:
        tuple: A tuple containing (start_date, end_date) as datetime objects.
    """
    today = datetime.now()

    # Get the first day of the current month
    first_day_current_month = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    # Get the last day of the previous month
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


def get_audit_transactions(
    start_date=None, end_date=None, account_number=None, material_id=None
):
    """
    Get audit transactions data for the specified date range and filters.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to first day of previous month.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to last day of previous month.
        account_number (str, optional): Filter by GL account number.
        material_id (str, optional): Filter by material ID.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Convert dates to strings for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Start building parameter list with dates
    params = [start_date_str, end_date_str]

    # Build the base query
    query = """
    SELECT TH.TRANSACTIONID,
        TH.TRANSDATETIME,
        TH.TRANSTYPE,
        TH.PERSONNEL,
        ISS.WORKORDERID AS ISSUE_WORKORDERID,
        RCV.WORKORDERID AS RECEIVE_WORKORDERID,
        TH.MATERIALUID,
        ML.DESCRIPTION,
        MA.OLDQUANT,
        MA.NEWQUANT,
        MA.OLDUNITCOST,
        MA.NEWUNITCOST,
        MA.ACCTNUM,
        MA.COSTDIFF
    FROM [azteca].[MATAUDIT] MA
    INNER JOIN [azteca].[TRANSHISTORY] TH
        ON MA.TRANSACTIONID = TH.TRANSACTIONID
    INNER JOIN [azteca].[MATERIALLEAF] ML
        ON TH.MATERIALSID = ML.MATERIALSID
    LEFT JOIN [azteca].[ISSUE] ISS
        ON TH.TRANSACTIONID = ISS.TRANSACTIONID
    LEFT JOIN [azteca].[RECEIVE] RCV
        ON TH.TRANSACTIONID = RCV.TRANSACTIONID
    WHERE TH.TRANSDATETIME BETWEEN ? AND ?
    """

    # Add filters if provided
    if account_number:
        query += " AND MA.ACCTNUM = ?"
        params.append(account_number)

    if material_id:
        query += " AND TH.MATERIALUID = ?"
        params.append(material_id)

    # Add ordering
    query += """
    ORDER BY MA.ACCTNUM,
        TH.MATERIALUID
    """

    logger.info(
        "Generated audit transactions query for period %s to %s with filters: account=%s, material=%s",
        start_date_str,
        end_date_str,
        account_number or "None",
        material_id or "None",
    )

    return query, tuple(params), "cw"  # Using the CityWorks database


def get_account_summary(start_date=None, end_date=None):
    """
    Get summary of transactions by account number.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to first day of previous month.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to last day of previous month.

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
        ISNULL(MA.ACCTNUM, 'MISSING') AS ACCTNUM,
        COUNT(DISTINCT TH.TRANSACTIONID) AS TransactionCount,
        COUNT(DISTINCT TH.MATERIALUID) AS MaterialCount,
        SUM(ABS(MA.COSTDIFF)) AS TotalCostDiff
    FROM [azteca].[MATAUDIT] MA
    INNER JOIN [azteca].[TRANSHISTORY] TH
        ON MA.TRANSACTIONID = TH.TRANSACTIONID
    WHERE TH.TRANSDATETIME BETWEEN ? AND ?
    GROUP BY MA.ACCTNUM
    ORDER BY SUM(ABS(MA.COSTDIFF)) DESC
    """

    logger.info(
        "Generated account summary query for period %s to %s",
        start_date_str,
        end_date_str,
    )

    return query, tuple(params), "cw"  # Using the CityWorks database


def get_material_summary(start_date=None, end_date=None):
    """
    Get summary of transactions by material.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to first day of previous month.
        end_date (datetime, optional): End date for the report period.
            If None, defaults to last day of previous month.

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
        TH.MATERIALUID,
        ML.DESCRIPTION,
        COUNT(DISTINCT TH.TRANSACTIONID) AS TransactionCount,
        SUM(ABS(MA.COSTDIFF)) AS TotalCostDiff,
        MIN(MA.OLDUNITCOST) AS MinOldCost,
        MAX(MA.NEWUNITCOST) AS MaxNewCost,
        AVG(MA.NEWUNITCOST) AS AvgNewCost
    FROM [azteca].[MATAUDIT] MA
    INNER JOIN [azteca].[TRANSHISTORY] TH
        ON MA.TRANSACTIONID = TH.TRANSACTIONID
    INNER JOIN [azteca].[MATERIALLEAF] ML
        ON TH.MATERIALSID = ML.MATERIALSID
    WHERE TH.TRANSDATETIME BETWEEN ? AND ?
    GROUP BY TH.MATERIALUID, ML.DESCRIPTION
    ORDER BY SUM(ABS(MA.COSTDIFF)) DESC
    """

    logger.info(
        "Generated material summary query for period %s to %s",
        start_date_str,
        end_date_str,
    )

    return query, tuple(params), "cw"  # Using the CityWorks database
