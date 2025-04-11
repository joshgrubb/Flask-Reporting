"""
Cash Only Accounts SQL Queries.

This module contains the SQL queries used in the Cash Only Accounts report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)


def get_cash_only_accounts():
    """
    Get accounts with active 'Cash Only Account' internal messages.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT ua.UtilityAccountID,
        ua.FullAccountNumber,
        uaim.MessageStartDate,
        uaim.MessageEndDate,
        uaim.InternalMessageID,
        utim.Message
    FROM [LogosDB].[dbo].[UtilityAccountInternalMessages] uaim
    INNER JOIN [LogosDB].[dbo].[UTInternalMessages] utim
        ON utim.InternalMessageID = uaim.InternalMessageID
    INNER JOIN [LogosDB].[dbo].[UtilityAccount] ua
        ON ua.UtilityAccountID = uaim.UtilityAccountID
    WHERE (
            uaim.MessageEndDate IS NULL
            OR uaim.MessageEndDate >= GETDATE()
            )
        AND uaim.InternalMessageID = 9  -- Cash Only Account
        AND ua.AccountStatus <> 2  -- Exclude inactive/closed accounts
    ORDER BY uaim.MessageStartDate
    """

    logger.info("Generated cash only accounts query")
    return query, (), "nws"


def get_cash_only_accounts_summary():
    """
    Get summary statistics for cash only accounts.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT 
        COUNT(*) AS TotalAccounts,
        MIN(uaim.MessageStartDate) AS OldestMessageDate,
        MAX(uaim.MessageStartDate) AS NewestMessageDate,
        SUM(CASE WHEN uaim.MessageEndDate IS NULL THEN 1 ELSE 0 END) AS NoEndDateCount,
        DATEDIFF(day, MIN(uaim.MessageStartDate), GETDATE()) AS DaysSinceOldest
    FROM [LogosDB].[dbo].[UtilityAccountInternalMessages] uaim
    INNER JOIN [LogosDB].[dbo].[UTInternalMessages] utim
        ON utim.InternalMessageID = uaim.InternalMessageID
    INNER JOIN [LogosDB].[dbo].[UtilityAccount] ua
        ON ua.UtilityAccountID = uaim.UtilityAccountID
    WHERE (
            uaim.MessageEndDate IS NULL
            OR uaim.MessageEndDate >= GETDATE()
            )
        AND uaim.InternalMessageID = 9  -- Cash Only Account
        AND ua.AccountStatus <> 2  -- Exclude inactive/closed accounts
    """

    logger.info("Generated cash only accounts summary query")
    return query, (), "nws"


def get_accounts_by_date_range(start_date=None, end_date=None):
    """
    Get cash only accounts based on a date range of message start dates.

    Args:
        start_date (datetime, optional): Start date for filtering.
        end_date (datetime, optional): End date for filtering.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    params = []
    where_clauses = [
        "(uaim.MessageEndDate IS NULL OR uaim.MessageEndDate >= GETDATE())",
        "uaim.InternalMessageID = 9",  # Cash Only Account
        "ua.AccountStatus <> 2",  # Exclude inactive/closed accounts
    ]

    if start_date:
        where_clauses.append("uaim.MessageStartDate >= ?")
        params.append(start_date)

    if end_date:
        where_clauses.append("uaim.MessageStartDate <= ?")
        params.append(end_date)

    where_clause = " AND ".join(where_clauses)

    query = f"""
    SELECT ua.UtilityAccountID,
        ua.FullAccountNumber,
        uaim.MessageStartDate,
        uaim.MessageEndDate,
        uaim.InternalMessageID,
        utim.Message
    FROM [LogosDB].[dbo].[UtilityAccountInternalMessages] uaim
    INNER JOIN [LogosDB].[dbo].[UTInternalMessages] utim
        ON utim.InternalMessageID = uaim.InternalMessageID
    INNER JOIN [LogosDB].[dbo].[UtilityAccount] ua
        ON ua.UtilityAccountID = uaim.UtilityAccountID
    WHERE {where_clause}
    ORDER BY uaim.MessageStartDate
    """

    logger.info(
        "Generated cash only accounts query with date range: %s to %s",
        start_date,
        end_date,
    )
    return query, tuple(params), "nws"
