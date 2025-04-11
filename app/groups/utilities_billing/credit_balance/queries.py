"""
Credit Balance SQL Queries.

This module contains the SQL queries used in the Credit Balance report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)


def get_credit_balance_accounts():
    """
    Get accounts with credit balances (negative balance amounts).

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # SQL query using CTEs for calculating balances
    query = """
    -- Calculate the overall balance per UtilityAccountID from various sources
    WITH BalanceCTE
    AS (
        SELECT UtilityAccountID,
            SUM(TransAmount) AS Balance
        FROM (
            -- Sum for UtilityTransactionSummary amounts
            SELECT UTS.UtilityAccountID,
                SUM(UTS.TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary UTS
            INNER JOIN UtilityTransactionHeader UTH
                ON UTH.UTTransHeaderID = UTS.UTTransheaderID
            GROUP BY UTS.UtilityAccountID
            
            UNION ALL
            
            -- Sum for Utility Payment amounts (multiplied by -1)
            SELECT H.UtilityAccountID,
                SUM(H.Amount * - 1) AS TransAmount
            FROM Utilitypaymentheader H
            WHERE H.UtilityOverPaymentID IS NULL
                AND H.ProcessStatus <> 3
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            -- Sum for Utility Adjustments (non-penalty adjustments)
            SELECT H.UtilityAccountID,
                SUM(H.AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader H
            WHERE H.UtilityAccountID IS NOT NULL
                AND H.AdjustmentType <> 5
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            -- Sum for UtilityTransactionSummary amounts with ExceptionBillID
            SELECT UtilityAccountID,
                SUM(TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary
            WHERE ExceptionBillID IS NOT NULL
            GROUP BY UtilityAccountID
            
            UNION ALL
            
            -- Sum for Utility Adjustments that are of penalty type (AdjustmentType = 5)
            SELECT UtilityAccountID,
                SUM(AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader
            WHERE UtilityAccountID IS NOT NULL
                AND AdjustmentType = 5
            GROUP BY UtilityAccountID
            ) AS x
        GROUP BY UtilityAccountID
        ),
        -- Main query that gathers account information and applies business logic
    AccountData
    AS (
        SELECT DISTINCT UA.FullAccountNumber,
            UA.MoveOutDate,
            CAST(B.Balance AS DECIMAL(10, 2)) AS LastBalance,
            C.FormalName,
            A.FullAddress,
            UCN.EmailAddress,
            UCN.CellPhone,
            C.PrimaryPhone,
            -- Note: The derived column [Exempt from Penalty] is computed but not returned in the final result set.
            CASE 
                WHEN UA.ExemptFromPenaltyFlag = 1
                    THEN 'Some Exemptions'
                ELSE 'Not Exempt'
                END AS [Exempt from Penalty],
            CASE 
                WHEN UA.AccountStatus = 1
                    THEN 'Active'
                ELSE 'INACTIVE'
                END AS AccountStatus
        FROM UtilityAccount UA
        -- Join to transaction-related tables (left joins may produce duplicate rows, hence DISTINCT above)
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
        -- Join to customer and central name data; ensuring to grab only the primary account
        INNER JOIN UtilityCustomerAccount UCA
            ON UCA.UtilityAccountID = UA.UtilityAccountID
                AND UCA.PrimaryFlag = 1
        INNER JOIN UtilityCentralName UCN
            ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
        LEFT JOIN CentralName C
            ON C.CentralNameID = UCN.CentralNameID
        -- Join to address information via the PMCentralServiceAddress relationship
        LEFT JOIN PMCentralServiceAddress PMC
            ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
        INNER JOIN Address A
            ON A.AddressID = PMC.AddressID
        -- Bring in the calculated balance
        LEFT JOIN BalanceCTE B
            ON B.UtilityAccountID = UA.UtilityAccountID
        WHERE
            -- Filter on the underlying UtilityAccount status (exclude active accounts)
            UA.AccountStatus <> 1
            -- Only include records linked to a valid BillingProfile
            AND BF.BillingProfileID IS NOT NULL
        )
    -- Final select filters negative balances and orders results
    SELECT FullAccountNumber,
        LastBalance,
        FormalName,
        FullAddress,
        EmailAddress,
        MoveOutDate,
        CellPhone,
        PrimaryPhone,
        AccountStatus
    FROM AccountData
    WHERE LastBalance < 0.00
    ORDER BY MoveOutDate DESC;
    """

    logger.info("Generated credit balance accounts query")
    return query, (), "nws"


def get_credit_balance_summary():
    """
    Get summary statistics for credit balance accounts.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    -- Calculate the overall balance per UtilityAccountID from various sources
    WITH BalanceCTE
    AS (
        SELECT UtilityAccountID,
            SUM(TransAmount) AS Balance
        FROM (
            -- Sum for UtilityTransactionSummary amounts
            SELECT UTS.UtilityAccountID,
                SUM(UTS.TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary UTS
            INNER JOIN UtilityTransactionHeader UTH
                ON UTH.UTTransHeaderID = UTS.UTTransheaderID
            GROUP BY UTS.UtilityAccountID
            
            UNION ALL
            
            -- Sum for Utility Payment amounts (multiplied by -1)
            SELECT H.UtilityAccountID,
                SUM(H.Amount * - 1) AS TransAmount
            FROM Utilitypaymentheader H
            WHERE H.UtilityOverPaymentID IS NULL
                AND H.ProcessStatus <> 3
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            -- Sum for Utility Adjustments (non-penalty adjustments)
            SELECT H.UtilityAccountID,
                SUM(H.AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader H
            WHERE H.UtilityAccountID IS NOT NULL
                AND H.AdjustmentType <> 5
            GROUP BY H.UtilityAccountID
            
            UNION ALL
            
            -- Sum for UtilityTransactionSummary amounts with ExceptionBillID
            SELECT UtilityAccountID,
                SUM(TransSummaryAmount) AS TransAmount
            FROM UtilityTransactionSummary
            WHERE ExceptionBillID IS NOT NULL
            GROUP BY UtilityAccountID
            
            UNION ALL
            
            -- Sum for Utility Adjustments that are of penalty type (AdjustmentType = 5)
            SELECT UtilityAccountID,
                SUM(AdjustmentAmount) AS TransAmount
            FROM UtilityAdjustmentHeader
            WHERE UtilityAccountID IS NOT NULL
                AND AdjustmentType = 5
            GROUP BY UtilityAccountID
            ) AS x
        GROUP BY UtilityAccountID
        ),
    -- Select summary information
    SummaryData AS (
        SELECT 
            COUNT(*) AS TotalAccounts,
            SUM(ABS(Balance)) AS TotalCreditAmount,
            AVG(ABS(Balance)) AS AvgCreditAmount,
            MIN(ABS(Balance)) AS MinCreditAmount,
            MAX(ABS(Balance)) AS MaxCreditAmount
        FROM BalanceCTE
        WHERE Balance < 0
    )
    SELECT * FROM SummaryData;
    """

    logger.info("Generated credit balance summary query")
    return query, (), "nws"
