"""
Late Fees SQL Queries.

This module contains the SQL queries used in the Late Fees report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from typing import Optional, Tuple, List, Any

# Configure logger
logger = logging.getLogger(__name__)


def get_late_fees_accounts(billing_profile_id: str) -> Tuple[str, tuple, str]:
    """
    Get accounts eligible for late fees for a specific billing profile.

    Args:
        billing_profile_id (str): The ID of the billing profile to filter accounts.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Parameters
    params = [billing_profile_id]

    # SQL query using Common Table Expressions (CTEs)
    query = """
    -- CTE to centralize the balance calculation
    WITH cteBalance
    AS (
        SELECT UtilityAccountID,
            SUM(TransAmount) AS Balance
        FROM (
            SELECT UTS.UtilityAccountID,
                SUM(TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary UTS
            INNER JOIN UtilityTransactionHeader UTH
                ON UTH.UTTransHeaderID = UTS.UTTransHeaderID
            GROUP BY UTS.UtilityAccountID
            
            UNION ALL
            
            SELECT H.UtilityAccountID,
                SUM(Amount * - 1) AS TransAmount
            FROM UtilityPaymentHeader H
            WHERE UtilityOverPaymentID IS NULL
                AND ProcessStatus <> 3
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            SELECT H.UtilityAccountID,
                SUM(AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader H
            WHERE UtilityAccountID IS NOT NULL
                AND AdjustmentType <> 5
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            SELECT UtilityAccountID,
                SUM(TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary
            WHERE ExceptionBillID IS NOT NULL
            GROUP BY UtilityAccountID
            
            UNION ALL
            
            SELECT UtilityAccountID,
                SUM(AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader
            WHERE UtilityAccountID IS NOT NULL
                AND AdjustmentType = 5
            GROUP BY UtilityAccountID
            ) AS x
        GROUP BY UtilityAccountID
        ),
        -- CTE for the common query structure
    cteRecords
    AS (
        SELECT DISTINCT BF.BillingProfileID,
            BF.BillingProfileCode,
            UA.FullAccountNumber,
            CAST(b.Balance AS DECIMAL(10, 2)) AS Balance,
            CAST(BM.EventDate AS DATE) AS CurrentDueDate,
            C.FormalName,
            UCN.EmailAddress,
            CAST(UCN.CellPhone AS BIGINT) AS CellPhone,
            CAST(C.PrimaryPhone AS BIGINT) AS PrimaryPhone,
            CAST(UCN.WorkPhone AS BIGINT) AS WorkPhone,
            CASE UA.ExemptFromPenaltyFlag
                WHEN 1
                    THEN 'Some Exemptions'
                ELSE 'Not Exempt'
                END AS [Exempt from Penalty],
            CASE UA.AccountStatus
                WHEN 1
                    THEN 'Active'
                ELSE 'INACTIVE'
                END AS AccountStatus,
            -- Additional columns for internal filtering
            UA.AccountStatus AS UA_AccountStatus,
            UA.ExemptFromPenaltyFlag AS UA_ExemptFlag,
            BB.BudgetBillEndDate
        FROM UtilityAccount UA
        LEFT JOIN UtilityTransactionSummary S
            ON S.UtilityAccountID = UA.UtilityAccountID
        LEFT JOIN UtilityTransactionHeader H
            ON H.UTTransHeaderID = S.UTTransHeaderID
        LEFT JOIN BillingManager BM
            ON BM.BillingCycleID = H.BillingCycleID
        LEFT JOIN BillingCycle BC
            ON BC.BillingCycleID = BM.BillingCycleID
        LEFT JOIN BillingProfile BF
            ON BF.BillingProfileID = BC.BillingProfileID
                AND BM.BillingEventType = 5
        INNER JOIN UtilityCustomerAccount UCA
            ON UCA.UtilityAccountID = UA.UtilityAccountID
                AND UCA.PrimaryFlag = 1
        INNER JOIN UtilityCentralName UCN
            ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
        LEFT JOIN CentralName C
            ON C.CentralNameID = UCN.CentralNameID
        LEFT JOIN UTBudgetBillHeader BB
            ON BB.UtilityAccountID = UA.UtilityAccountID
        LEFT JOIN dbo.UTBudgetBillDetail BBD
            ON BBD.BudgetBillID = BB.BudgetBillID
        LEFT JOIN cteBalance b
            ON b.UtilityAccountID = UA.UtilityAccountID
        WHERE BF.BillingProfileID = ?
            AND b.Balance > 5
            AND BM.EventDate BETWEEN DATEADD(DAY, - 29, GETDATE())
                AND GETDATE()
            AND S.PaidInFullDate IS NULL
        )
    -- Final result: select records meeting the first set of conditions
    -- and exclude those where BudgetBillEndDate is in the future.
    SELECT BillingProfileID,
        BillingProfileCode,
        FullAccountNumber,
        Balance,
        CurrentDueDate,
        FormalName,
        EmailAddress,
        CellPhone,
        PrimaryPhone,
        WorkPhone,
        [Exempt from Penalty],
        AccountStatus
    FROM cteRecords
    WHERE UA_AccountStatus = 1
        AND UA_ExemptFlag <> 1

    EXCEPT

    SELECT BillingProfileID,
        BillingProfileCode,
        FullAccountNumber,
        Balance,
        CurrentDueDate,
        FormalName,
        EmailAddress,
        CellPhone,
        PrimaryPhone,
        WorkPhone,
        [Exempt from Penalty],
        AccountStatus
    FROM cteRecords
    WHERE BudgetBillEndDate > GETDATE()
    ORDER BY FullAccountNumber
    """

    logger.info(
        "Generated late fees accounts query for billing profile ID: %s",
        billing_profile_id,
    )
    return query, tuple(params), "nws"


def get_billing_profiles() -> Tuple[str, tuple, str]:
    """
    Get all billing profiles to populate the selection dropdown.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT BillingProfileID, 
           BillingProfileCode, 
           BillingProfileDescription
    FROM BillingProfile
    WHERE InactiveFlag = 0
    ORDER BY BillingProfileCode
    """

    logger.info("Generated query for active billing profiles")
    return query, (), "nws"


def get_late_fees_summary(billing_profile_id: str) -> Tuple[str, tuple, str]:
    """
    Get summary statistics for late fees accounts.

    Args:
        billing_profile_id (str): The ID of the billing profile to filter accounts.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Parameters
    params = [billing_profile_id]

    # Build query for summary statistics
    query = """
    -- CTE to centralize the balance calculation
    WITH cteBalance
    AS (
        SELECT UtilityAccountID,
            SUM(TransAmount) AS Balance
        FROM (
            SELECT UTS.UtilityAccountID,
                SUM(TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary UTS
            INNER JOIN UtilityTransactionHeader UTH
                ON UTH.UTTransHeaderID = UTS.UTTransHeaderID
            GROUP BY UTS.UtilityAccountID
            
            UNION ALL
            
            SELECT H.UtilityAccountID,
                SUM(Amount * - 1) AS TransAmount
            FROM UtilityPaymentHeader H
            WHERE UtilityOverPaymentID IS NULL
                AND ProcessStatus <> 3
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            SELECT H.UtilityAccountID,
                SUM(AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader H
            WHERE UtilityAccountID IS NOT NULL
                AND AdjustmentType <> 5
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            SELECT UtilityAccountID,
                SUM(TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary
            WHERE ExceptionBillID IS NOT NULL
            GROUP BY UtilityAccountID
            
            UNION ALL
            
            SELECT UtilityAccountID,
                SUM(AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader
            WHERE UtilityAccountID IS NOT NULL
                AND AdjustmentType = 5
            GROUP BY UtilityAccountID
            ) AS x
        GROUP BY UtilityAccountID
        ),
    -- Get the filtered records that are eligible for late fees
    cteEligibleAccounts AS (
        SELECT UA.UtilityAccountID,
               BF.BillingProfileID,
               BF.BillingProfileCode,
               CAST(b.Balance AS DECIMAL(10, 2)) AS Balance
        FROM UtilityAccount UA
        LEFT JOIN UtilityTransactionSummary S
            ON S.UtilityAccountID = UA.UtilityAccountID
        LEFT JOIN UtilityTransactionHeader H
            ON H.UTTransHeaderID = S.UTTransHeaderID
        LEFT JOIN BillingManager BM
            ON BM.BillingCycleID = H.BillingCycleID
        LEFT JOIN BillingCycle BC
            ON BC.BillingCycleID = BM.BillingCycleID
        LEFT JOIN BillingProfile BF
            ON BF.BillingProfileID = BC.BillingProfileID
                AND BM.BillingEventType = 5
        LEFT JOIN cteBalance b
            ON b.UtilityAccountID = UA.UtilityAccountID
        LEFT JOIN UTBudgetBillHeader BB
            ON BB.UtilityAccountID = UA.UtilityAccountID
        WHERE BF.BillingProfileID = ?
            AND b.Balance > 5
            AND BM.EventDate BETWEEN DATEADD(DAY, - 29, GETDATE())
                AND GETDATE()
            AND S.PaidInFullDate IS NULL
            AND UA.AccountStatus = 1
            AND UA.ExemptFromPenaltyFlag <> 1
            AND (BB.BudgetBillEndDate IS NULL OR BB.BudgetBillEndDate <= GETDATE())
    )
    -- Generate summary statistics
    SELECT 
        COUNT(*) AS TotalAccounts,
        SUM(Balance) AS TotalBalance,
        AVG(Balance) AS AverageBalance,
        MIN(Balance) AS MinimumBalance,
        MAX(Balance) AS MaximumBalance,
        BillingProfileCode,
        BillingProfileID
    FROM cteEligibleAccounts
    GROUP BY BillingProfileCode, BillingProfileID
    """

    logger.info(
        "Generated late fees summary query for billing profile ID: %s",
        billing_profile_id,
    )
    return query, tuple(params), "nws"
