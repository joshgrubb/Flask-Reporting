"""
High Balance SQL Queries.

This module contains the SQL queries used in the High Balance report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from typing import Tuple, List, Optional, Any, Dict, Union

# Configure logger
logger = logging.getLogger(__name__)


def get_high_balance_accounts(
    balance_threshold: float, account_types: List[str]
) -> Tuple[str, tuple, str]:
    """
    Get accounts with balances higher than the specified threshold.

    Args:
        balance_threshold (float): The minimum balance threshold to filter accounts.
        account_types (List[str]): List of account types to include (e.g., ["477"] for Residential).

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Prepare parameters
    params = [balance_threshold]

    # Build account type filter
    if not account_types:
        # Default to residential (477) if no types are specified
        account_types = ["477"]

    # Create placeholders for account types
    account_type_placeholders = ", ".join(["?"] * len(account_types))
    params.extend(account_types)

    # Build the query
    query = f"""
    WITH UtilityAccountData
    AS (
        SELECT UA.UtilityAccountID,
            UA.FullAccountNumber,
            [UT].[GetUtilityAccountBalanceForReceiptSlip](UA.UtilityAccountID) AS Balance,
            UA.vsAccountType,
            UA.PMCentralServiceAddressID
        FROM UtilityAccount UA
        WHERE UA.AccountStatus <> 2
        )
    SELECT UAD.UtilityAccountID,
        UAD.FullAccountNumber,
        UAD.Balance,
        UAD.vsAccountType,
        VSE.EntryValue AS AccountType,
        A.FullAddress,
        CN.LastName,
        CN.FirstName,
        UCN.EmailAddress,
        CN.PrimaryPhone
    FROM UtilityAccountData UAD
    INNER JOIN PMCentralServiceAddress PMC
        ON PMC.PMCentralServiceAddressID = UAD.PMCentralServiceAddressID
    INNER JOIN Address A
        ON A.AddressID = PMC.AddressID
    LEFT JOIN ValidationSetEntry VSE
        ON VSE.EntryID = UAD.vsAccountType
    LEFT JOIN UtilityCustomerAccount UCA
        ON UCA.UtilityAccountID = UAD.UtilityAccountID
        AND UCA.PrimaryFlag = 1
    LEFT JOIN UtilityCentralName UCN
        ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
    LEFT JOIN CentralName CN
        ON CN.CentralNameID = UCN.CentralNameID
    WHERE UAD.Balance > ?
        AND UAD.vsAccountType IN ({account_type_placeholders})
        AND NOT EXISTS (
            -- Exclude UtilityAccountIDs with active budget bills
            SELECT 1
            FROM UTBudgetBillHeader BB
            WHERE BB.UtilityAccountID = UAD.UtilityAccountID
                AND BB.BudgetBillEndDate >= GETDATE()
            )
    ORDER BY UAD.Balance DESC;
    """

    logger.info(
        "Generated high balance query with threshold: %.2f and account types: %s",
        balance_threshold,
        ", ".join(account_types),
    )
    return query, tuple(params), "nws"


def get_account_type_options() -> Tuple[str, tuple, str]:
    """
    Get available account types for the filter dropdown.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT DISTINCT VSE.EntryID AS TypeID,
        VSE.EntryValue AS TypeName
    FROM ValidationSetEntry VSE
    WHERE VSE.SetID = 102
    ORDER BY VSE.EntryValue
    """

    logger.info("Getting available account types for filter")
    return query, (), "nws"


def get_high_balance_summary(
    balance_threshold: float, account_types: List[str]
) -> Tuple[str, tuple, str]:
    """
    Get summary statistics for high balance accounts.

    Args:
        balance_threshold (float): The minimum balance threshold to filter accounts.
        account_types (List[str]): List of account types to include.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Prepare parameters
    params = [balance_threshold]

    # Build account type filter
    if not account_types:
        # Default to residential (477) if no types are specified
        account_types = ["477"]

    # Create placeholders for account types
    account_type_placeholders = ", ".join(["?"] * len(account_types))
    params.extend(account_types)

    # Build the query
    query = f"""
    WITH UtilityAccountData
    AS (
        SELECT UA.UtilityAccountID,
            UA.FullAccountNumber,
            [UT].[GetUtilityAccountBalanceForReceiptSlip](UA.UtilityAccountID) AS Balance,
            UA.vsAccountType,
            UA.PMCentralServiceAddressID
        FROM UtilityAccount UA
        WHERE UA.AccountStatus <> 2
        )
    SELECT 
        COUNT(*) AS TotalAccounts,
        SUM(UAD.Balance) AS TotalBalance,
        AVG(UAD.Balance) AS AverageBalance,
        MAX(UAD.Balance) AS MaxBalance,
        MIN(UAD.Balance) AS MinBalance,
        VSE.EntryValue AS AccountType,
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS Percentage
    FROM UtilityAccountData UAD
    LEFT JOIN ValidationSetEntry VSE
        ON VSE.EntryID = UAD.vsAccountType
    WHERE UAD.Balance > ?
        AND UAD.vsAccountType IN ({account_type_placeholders})
        AND NOT EXISTS (
            -- Exclude UtilityAccountIDs with active budget bills
            SELECT 1
            FROM UTBudgetBillHeader BB
            WHERE BB.UtilityAccountID = UAD.UtilityAccountID
                AND BB.BudgetBillEndDate >= GETDATE()
            )
    GROUP BY VSE.EntryValue
    ORDER BY COUNT(*) DESC
    """

    logger.info(
        "Generated high balance summary query with threshold: %.2f and account types: %s",
        balance_threshold,
        ", ".join(account_types),
    )
    return query, tuple(params), "nws"
