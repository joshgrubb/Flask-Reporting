"""
New Customer Accounts SQL Queries.

This module contains the SQL queries used in the New Customer Accounts report.
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
    # Format as date only to ensure consistent comparison in SQL
    return date_obj.strftime("%Y-%m-%d")


def get_new_customer_accounts(move_in_date=None):
    """
    Get new customer accounts data.

    Args:
        move_in_date (datetime, optional): Minimum move-in date to filter accounts.
            If None, defaults to 30 days ago.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Use default date if not provided
    if move_in_date is None:
        move_in_date = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0
        )

    # Convert date to string for SQL
    move_in_date_str = format_date_for_query(move_in_date)

    # Parameters
    params = [move_in_date_str]

    # Build the query based on the DAX query
    query = """
    SELECT 
        UA.FullAccountNumber,
        VSE.[Description] AS 'Account Type',
        CN.LastName,
        CN.FirstName,
        UCN.EmailAddress,
        A.FullAddress,
        UA.MoveInDate,
        UA.AccountOpenDate
    FROM 
        [LogosDB].[dbo].[UtilityAccount] UA
    INNER JOIN 
        [LogosDB].[dbo].[UtilityCustomerAccount] UCA ON UA.UtilityAccountID = UCA.UtilityAccountID
    INNER JOIN 
        [LogosDB].[dbo].[UtilityCentralName] UCN ON UCA.UtilityCentralNameID = UCN.UtilityCentralNameID
    INNER JOIN 
        [LogosDB].[dbo].[CentralName] CN ON UCN.CentralNameID = CN.CentralNameID
    INNER JOIN 
        [LogosDB].[dbo].[PMCentralServiceAddress] PMCSA ON UA.PMCentralServiceAddressID = PMCSA.PMCentralServiceAddressID
    INNER JOIN 
        [LogosDB].[dbo].[Address] A ON PMCSA.AddressID = A.AddressID
    LEFT JOIN 
        [LogosDB].[dbo].[ValidationSetEntry] VSE ON UA.vsAccountType = VSE.EntryID
    WHERE 
        CONVERT(date, UA.MoveInDate) >= CONVERT(date, ?)
        AND UCA.PrimaryFlag = 1
        AND (
            UA.FullAccountNumber IS NOT NULL OR
            UA.vsAccountType IS NOT NULL OR
            CN.LastName IS NOT NULL OR
            CN.FirstName IS NOT NULL OR
            UCN.EmailAddress IS NOT NULL OR
            A.FullAddress IS NOT NULL OR
            UA.MoveInDate IS NOT NULL OR
            UA.AccountOpenDate IS NOT NULL
        )
    ORDER BY
        UA.FullAccountNumber,
        VSE.[Description],
        CN.LastName,
        CN.FirstName,
        UCN.EmailAddress,
        A.FullAddress,
        UA.MoveInDate,
        UA.AccountOpenDate
    """

    logger.info(
        f"Generated new customer accounts query with move-in date >= {move_in_date_str}"
    )
    return query, tuple(params), "nws"


def get_account_type_summary(move_in_date=None):
    """
    Get summary of account types for new customer accounts.

    Args:
        move_in_date (datetime, optional): Minimum move-in date to filter accounts.
            If None, defaults to 30 days ago.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Use default date if not provided
    if move_in_date is None:
        move_in_date = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0
        )

    # Convert date to string for SQL
    move_in_date_str = format_date_for_query(move_in_date)

    # Parameters
    params = [move_in_date_str]

    # Build the query
    query = """
    SELECT 
        VSE.[Description] AS 'Account Type',
        COUNT(*) AS AccountCount
    FROM 
        [LogosDB].[dbo].[UtilityAccount] UA
    INNER JOIN 
        [LogosDB].[dbo].[UtilityCustomerAccount] UCA ON UA.UtilityAccountID = UCA.UtilityAccountID
    LEFT JOIN 
        [LogosDB].[dbo].[ValidationSetEntry] VSE ON UA.vsAccountType = VSE.EntryID
    WHERE 
        CONVERT(date, UA.MoveInDate) >= CONVERT(date, ?)
        AND UCA.PrimaryFlag = 1
    GROUP BY
        VSE.[Description]
    ORDER BY
        COUNT(*) DESC
    """

    logger.info(
        f"Generated account type summary query with move-in date >= {move_in_date_str}"
    )
    return query, tuple(params), "nws"


def get_daily_new_accounts(move_in_date=None):
    """
    Get daily count of new accounts.

    Args:
        move_in_date (datetime, optional): Minimum move-in date to filter accounts.
            If None, defaults to 30 days ago.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Use default date if not provided
    if move_in_date is None:
        move_in_date = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0
        )

    # Convert date to string for SQL
    move_in_date_str = format_date_for_query(move_in_date)

    # Parameters
    params = [move_in_date_str]

    # Build the query
    query = """
    SELECT 
        CONVERT(date, UA.MoveInDate) AS MoveInDate,
        COUNT(*) AS NewAccountCount
    FROM 
        [LogosDB].[dbo].[UtilityAccount] UA
    INNER JOIN 
        [LogosDB].[dbo].[UtilityCustomerAccount] UCA ON UA.UtilityAccountID = UCA.UtilityAccountID
    WHERE 
        CONVERT(date, UA.MoveInDate) >= CONVERT(date, ?)
        AND UCA.PrimaryFlag = 1
    GROUP BY
        CONVERT(date, UA.MoveInDate)
    ORDER BY
        CONVERT(date, UA.MoveInDate)
    """

    logger.info(
        f"Generated daily new accounts query with move-in date >= {move_in_date_str}"
    )
    return query, tuple(params), "nws"
