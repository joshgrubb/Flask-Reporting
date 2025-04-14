"""
Dollar Search SQL Queries.

This module contains the SQL queries used in the Dollar Search report.
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


def get_dollar_search(transaction_amount, start_date=None, end_date=None):
    """
    Get payment transactions that match a specific dollar amount.

    Args:
        transaction_amount (float): The specific amount to search for.
        start_date (datetime, optional): Start date for transaction search.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for transaction search.
            If None, defaults to current date.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Format dates for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Parameters
    params = [
        start_date_str,
        end_date_str,
        transaction_amount,
        start_date_str,
        end_date_str,
        transaction_amount,
        start_date_str,
        end_date_str,
        transaction_amount,
    ]

    # Build the query that combines payments from different sources
    query = """
    /* Utility Account Payments */
    SELECT UA.FullAccountNumber AS AccountOrRef,
        SUM(S.TransSummaryAmount) AS Amount,
        S.TransactionDate,
        'Utility Payment' AS PaymentType
    FROM UtilityAccount UA
    LEFT JOIN UtilityTransactionSummary S
        ON UA.UtilityAccountID = S.UtilityAccountID
    WHERE S.TransactionDate BETWEEN ?
            AND ?
    GROUP BY UA.FullAccountNumber,
        S.TransactionDate
    HAVING SUM(S.TransSummaryAmount) = ?
    
    UNION ALL
    
    /* Online Payments */
    SELECT D.ReferenceCode AS AccountOrRef,
        T.Amount AS Amount,
        T.TransactionDate,
        'Online Payment' AS PaymentType
    FROM [LogosDB].[ePay].[Transaction] T
    INNER JOIN epay.TransactionDetail D
        ON T.TransactionId = D.TransactionId
    WHERE T.TransactionDate BETWEEN ?
            AND ?
        AND T.Amount = ?
    
    UNION ALL
    
    /* Cash or Check Payments */
    SELECT (R.ReceiptNumber + '   ' + R.ReceivedFromName) AS AccountOrRef,
        RP.PaymentAmount AS Amount,
        R.PaymentDate AS TransactionDate,
        'Cash/Check Payment' AS PaymentType
    FROM dbo.Receipt R
    INNER JOIN ReceiptBatch RB
        ON R.ReceiptBatchID = RB.ReceiptBatchID
    INNER JOIN dbo.CollectionStation CS
        ON R.CollectionStationID = CS.CollectionStationID
    INNER JOIN dbo.SecurityUser SU
        ON R.CashierID = SU.UserID
    LEFT JOIN dbo.ReceiptPayment RP
        ON R.ReceiptID = RP.ReceiptID
    INNER JOIN dbo.ReceiptTransaction RT
        ON R.ReceiptID = RT.ReceiptID
    WHERE R.PaymentDate BETWEEN ?
            AND ?
        AND RP.PaymentAmount = ?

    ORDER BY TransactionDate DESC
    """

    logger.info(
        "Generated dollar search query for amount %.2f between %s and %s",
        transaction_amount,
        start_date_str,
        end_date_str,
    )
    return query, tuple(params), "nws"


def get_transaction_count(transaction_amount, start_date=None, end_date=None):
    """
    Get count of payment transactions that match a specific dollar amount.

    Args:
        transaction_amount (float): The specific amount to search for.
        start_date (datetime, optional): Start date for transaction search.
            If None, defaults to 30 days ago.
        end_date (datetime, optional): End date for transaction search.
            If None, defaults to current date.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default dates if not provided
    if start_date is None or end_date is None:
        start_date, end_date = get_default_date_range()

    # Format dates for SQL
    start_date_str = format_date_for_query(start_date)
    end_date_str = format_date_for_query(end_date)

    # Parameters
    params = [
        start_date_str,
        end_date_str,
        transaction_amount,
        start_date_str,
        end_date_str,
        transaction_amount,
        start_date_str,
        end_date_str,
        transaction_amount,
    ]

    # Build the query to count transactions by type
    query = """
    SELECT PaymentType, COUNT(*) AS TransactionCount
    FROM (
        /* Utility Account Payments */
        SELECT 'Utility Payment' AS PaymentType
        FROM UtilityAccount UA
        LEFT JOIN UtilityTransactionSummary S
            ON UA.UtilityAccountID = S.UtilityAccountID
        WHERE S.TransactionDate BETWEEN ?
                AND ?
        GROUP BY UA.FullAccountNumber,
            S.TransactionDate
        HAVING SUM(S.TransSummaryAmount) = ?
        
        UNION ALL
        
        /* Online Payments */
        SELECT 'Online Payment' AS PaymentType
        FROM [LogosDB].[ePay].[Transaction] T
        INNER JOIN epay.TransactionDetail D
            ON T.TransactionId = D.TransactionId
        WHERE T.TransactionDate BETWEEN ?
                AND ?
            AND T.Amount = ?
        
        UNION ALL
        
        /* Cash or Check Payments */
        SELECT 'Cash/Check Payment' AS PaymentType
        FROM dbo.Receipt R
        INNER JOIN ReceiptBatch RB
            ON R.ReceiptBatchID = RB.ReceiptBatchID
        INNER JOIN dbo.CollectionStation CS
            ON R.CollectionStationID = CS.CollectionStationID
        INNER JOIN dbo.SecurityUser SU
            ON R.CashierID = SU.UserID
        LEFT JOIN dbo.ReceiptPayment RP
            ON R.ReceiptID = RP.ReceiptID
        INNER JOIN dbo.ReceiptTransaction RT
            ON R.ReceiptID = RT.ReceiptID
        WHERE R.PaymentDate BETWEEN ?
                AND ?
            AND RP.PaymentAmount = ?
    ) AS CombinedResults
    GROUP BY PaymentType
    ORDER BY PaymentType
    """

    logger.info(
        "Generated transaction count query for amount %.2f between %s and %s",
        transaction_amount,
        start_date_str,
        end_date_str,
    )
    return query, tuple(params), "nws"
