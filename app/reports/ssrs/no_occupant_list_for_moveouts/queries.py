"""
No Occupant List for Moveouts SQL Queries.

This module contains the SQL queries used in the No Occupant List for Moveouts report.
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


def get_moveouts_without_occupants(start_date=None, end_date=None):
    """
    Get list of addresses with moveouts but no new occupants.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 90 days ago.
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

    # Build the query using CTE structure as provided
    query = """
    WITH CTE_AccountInfo
    AS (
        SELECT UA.FullAccountNumber,
            UA.AccountNumber,
            PMC.PMCentralServiceAddressID,
            MAX(UA.AccountNumberSequence + 1) AS AccountNext,
            UA.MoveOutDate,
            DATEDIFF(D, UA.MoveOutDate, GETDATE()) AS DaysFromMoveOut,
            A.FullAddress
        FROM UtilityAccount UA
        INNER JOIN PMCentralServiceAddress PMC
            ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
        INNER JOIN Address A
            ON A.AddressID = PMC.AddressID
        WHERE UA.MoveOutDate >= ?
            AND UA.MoveOutDate <= ?
        GROUP BY UA.AccountNumber,
            UA.FullAccountNumber,
            UA.AccountNumberSequence,
            UA.MoveOutDate,
            A.FullAddress,
            PMC.PMCentralServiceAddressID
        ),
    CTE_AccountNext
    AS (
        SELECT FullAccountNumber,
            AccountNumber,
            PMCentralServiceAddressID,
            AccountNumber + '-' + RIGHT('000' + CONVERT(VARCHAR, AccountNext, 0), 3) AS NEXT,
            MoveOutDate,
            DaysFromMoveOut,
            FullAddress
        FROM CTE_AccountInfo
        ),
    CTE_ExcludedAccounts
    AS (
        SELECT AccountNextDetails.FullAccountNumber,
            AccountNextDetails.DaysFromMoveOut,
            AccountNextDetails.FullAddress,
            AccountNextDetails.PMCentralServiceAddressID
        FROM CTE_AccountNext AccountNextDetails
        LEFT JOIN UtilityAccount UAA
            ON UAA.FullAccountNumber = AccountNextDetails.NEXT
        WHERE UAA.FullAccountNumber IS NULL
        )
    SELECT *
    FROM CTE_ExcludedAccounts ExcludedAccounts
    EXCEPT
    SELECT ExcludedAccounts.FullAccountNumber,
        ExcludedAccounts.DaysFromMoveOut,
        ExcludedAccounts.FullAddress,
        ExcludedAccounts.PMCentralServiceAddressID
    FROM CTE_ExcludedAccounts ExcludedAccounts
    INNER JOIN (
        SELECT PMCentralServiceAddressID
        FROM UtilityAccount
        WHERE AccountStatus = 1
        ) ActiveServiceAddresses
        ON ActiveServiceAddresses.PMCentralServiceAddressID = ExcludedAccounts.PMCentralServiceAddressID
    ORDER BY ExcludedAccounts.DaysFromMoveOut DESC
    """

    logger.info(
        f"Generated moveouts without occupants query for period {start_date_str} to {end_date_str}"
    )
    return query, tuple(params)


def get_moveouts_summary(start_date=None, end_date=None):
    """
    Get summary of moveouts without occupants by days since moveout.

    Args:
        start_date (datetime, optional): Start date for the report period.
            If None, defaults to 90 days ago.
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

    # Build the query using CTE structure
    # Fixed the ORDER BY to repeat the CASE expression instead of referring to AgeGroup alias
    query = """
    WITH CTE_AccountInfo
    AS (
        SELECT UA.FullAccountNumber,
            UA.AccountNumber,
            PMC.PMCentralServiceAddressID,
            MAX(UA.AccountNumberSequence + 1) AS AccountNext,
            UA.MoveOutDate,
            DATEDIFF(D, UA.MoveOutDate, GETDATE()) AS DaysFromMoveOut,
            A.FullAddress
        FROM UtilityAccount UA
        INNER JOIN PMCentralServiceAddress PMC
            ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
        INNER JOIN Address A
            ON A.AddressID = PMC.AddressID
        WHERE UA.MoveOutDate >= ?
            AND UA.MoveOutDate <= ?
        GROUP BY UA.AccountNumber,
            UA.FullAccountNumber,
            UA.AccountNumberSequence,
            UA.MoveOutDate,
            A.FullAddress,
            PMC.PMCentralServiceAddressID
        ),
    CTE_AccountNext
    AS (
        SELECT FullAccountNumber,
            AccountNumber,
            PMCentralServiceAddressID,
            AccountNumber + '-' + RIGHT('000' + CONVERT(VARCHAR, AccountNext, 0), 3) AS NEXT,
            MoveOutDate,
            DaysFromMoveOut,
            FullAddress
        FROM CTE_AccountInfo
        ),
    CTE_ExcludedAccounts
    AS (
        SELECT AccountNextDetails.FullAccountNumber,
            AccountNextDetails.DaysFromMoveOut,
            AccountNextDetails.FullAddress,
            AccountNextDetails.PMCentralServiceAddressID
        FROM CTE_AccountNext AccountNextDetails
        LEFT JOIN UtilityAccount UAA
            ON UAA.FullAccountNumber = AccountNextDetails.NEXT
        WHERE UAA.FullAccountNumber IS NULL
        ),
    CTE_FinalAccounts
    AS (
        SELECT *
        FROM CTE_ExcludedAccounts ExcludedAccounts
        EXCEPT
        SELECT ExcludedAccounts.FullAccountNumber,
            ExcludedAccounts.DaysFromMoveOut,
            ExcludedAccounts.FullAddress,
            ExcludedAccounts.PMCentralServiceAddressID
        FROM CTE_ExcludedAccounts ExcludedAccounts
        INNER JOIN (
            SELECT PMCentralServiceAddressID
            FROM UtilityAccount
            WHERE AccountStatus = 1
            ) ActiveServiceAddresses
            ON ActiveServiceAddresses.PMCentralServiceAddressID = ExcludedAccounts.PMCentralServiceAddressID
    )
    SELECT 
        CASE 
            WHEN DaysFromMoveOut <= 30 THEN '0-30 Days'
            WHEN DaysFromMoveOut <= 60 THEN '31-60 Days'
            WHEN DaysFromMoveOut <= 90 THEN '61-90 Days'
            ELSE 'Over 90 Days'
        END AS AgeGroup,
        COUNT(*) AS AddressCount
    FROM CTE_FinalAccounts
    GROUP BY
        CASE 
            WHEN DaysFromMoveOut <= 30 THEN '0-30 Days'
            WHEN DaysFromMoveOut <= 60 THEN '31-60 Days'
            WHEN DaysFromMoveOut <= 90 THEN '61-90 Days'
            ELSE 'Over 90 Days'
        END
    ORDER BY
        CASE 
            WHEN CASE 
                    WHEN DaysFromMoveOut <= 30 THEN '0-30 Days'
                    WHEN DaysFromMoveOut <= 60 THEN '31-60 Days'
                    WHEN DaysFromMoveOut <= 90 THEN '61-90 Days'
                    ELSE 'Over 90 Days'
                END = '0-30 Days' THEN 1
            WHEN CASE 
                    WHEN DaysFromMoveOut <= 30 THEN '0-30 Days'
                    WHEN DaysFromMoveOut <= 60 THEN '31-60 Days'
                    WHEN DaysFromMoveOut <= 90 THEN '61-90 Days'
                    ELSE 'Over 90 Days'
                END = '31-60 Days' THEN 2
            WHEN CASE 
                    WHEN DaysFromMoveOut <= 30 THEN '0-30 Days'
                    WHEN DaysFromMoveOut <= 60 THEN '31-60 Days'
                    WHEN DaysFromMoveOut <= 90 THEN '61-90 Days'
                    ELSE 'Over 90 Days'
                END = '61-90 Days' THEN 3
            ELSE 4
        END
    """

    logger.info(
        f"Generated moveouts summary query for period {start_date_str} to {end_date_str}"
    )
    return query, tuple(params)
