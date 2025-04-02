"""
Accounts No Garbage SQL Queries.

This module contains the SQL queries used in the Accounts No Garbage report.
Each function returns a SQL query string and optional parameters.
"""

import logging
from datetime import datetime, timedelta

# Configure logger
logger = logging.getLogger(__name__)


def get_accounts_no_garbage():
    """
    Get residential accounts with recent transactions but excluding
    those with garbage service (RateProfileMasterID 12 or 119).

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # SQL query using CTEs for clarity
    query = """
    WITH BaseTransactions AS (
        -- Retrieve accounts with recent transactions (using EOMONTH on a 31-day offset)
        SELECT DISTINCT
            UA.FullAccountNumber,
            CASE UA.vsAccountType
                WHEN '477' THEN 'Residential'
                WHEN '478' THEN 'Commercial'
                WHEN '479' THEN 'Industrial'
                WHEN '503' THEN 'Institutional'
            END AS AccountType,
            AA.FullAddress,
            AA.StreetName,
            C.LastName,
            C.FirstName
        FROM [LogosDB].[dbo].[UtilityTransactionDetail] AS UTD
        JOIN UtilityAccount AS UA
            ON UTD.UtilityAccountID = UA.UtilityAccountID
        JOIN RateComponents AS RC
            ON RC.RateComponentID = UTD.RateComponentID
        JOIN RateProfile AS p
            ON p.RateProfileID = RC.RateProfileID
        JOIN RateProfileMaster AS m
            ON m.RateProfileMasterID = p.RateProfileMasterID
        JOIN PMCentralServiceAddress AS PMC
            ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
        JOIN Address AS AA
            ON AA.AddressID = PMC.AddressID
        JOIN UtilityCustomerAccount AS UCA
            ON UCA.UtilityAccountID = UA.UtilityAccountID
        LEFT JOIN UtilityCentralName AS UCN
            ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
        LEFT JOIN CentralName AS C
            ON C.CentralNameID = UCN.CentralNameID
        WHERE UTD.TransactionDate >= EOMONTH(DATEADD(DAY, -31, GETDATE()))
          AND UA.vsAccountType = '477'
    ),
    ExcludedAccounts AS (
        -- Identify accounts that should be excluded because they have a
        -- transaction in the last 60 days with a RateProfileMasterID of '12' or '119'
        SELECT DISTINCT
            UA.FullAccountNumber,
            CASE UA.vsAccountType
                WHEN '477' THEN 'Residential'
                WHEN '478' THEN 'Commercial'
                WHEN '479' THEN 'Industrial'
                WHEN '503' THEN 'Institutional'
            END AS AccountType,
            AA.FullAddress,
            AA.StreetName,
            C.LastName,
            C.FirstName
        FROM UtilityAccount AS UA
        JOIN UtilityCustomerAccount AS UCA
            ON UCA.UtilityAccountID = UA.UtilityAccountID
        JOIN PMCentralServiceAddress AS PMC
            ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
        JOIN Address AS AA
            ON AA.AddressID = PMC.AddressID
        LEFT JOIN UtilityCentralName AS UCN
            ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
        LEFT JOIN CentralName AS C
            ON C.CentralNameID = UCN.CentralNameID
        WHERE UA.AccountCloseDate IS NULL
          AND EXISTS (
              SELECT 1
              FROM [LogosDB].[dbo].[UtilityTransactionDetail] AS UTD
              JOIN RateComponents AS RC
                  ON RC.RateComponentID = UTD.RateComponentID
              JOIN RateProfile AS p
                  ON p.RateProfileID = RC.RateProfileID
              WHERE UTD.UtilityAccountID = UA.UtilityAccountID
                AND UTD.TransactionDate >= DATEADD(DAY, -60, GETDATE())
                AND p.RateProfileMasterID IN ('12', '119')
          )
    )
    -- Return records from BaseTransactions except those in ExcludedAccounts
    SELECT *
    FROM BaseTransactions
    EXCEPT
    SELECT *
    FROM ExcludedAccounts
    ORDER BY StreetName;
    """

    logger.info("Generated accounts no garbage query")

    # No parameters for this query since it uses GETDATE() internally
    return query, ()


def get_street_summary():
    """
    Get summary of accounts by street without garbage service.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    query = """
    WITH BaseTransactions AS (
        -- Retrieve accounts with recent transactions (using EOMONTH on a 31-day offset)
        SELECT DISTINCT
            UA.FullAccountNumber,
            CASE UA.vsAccountType
                WHEN '477' THEN 'Residential'
                WHEN '478' THEN 'Commercial'
                WHEN '479' THEN 'Industrial'
                WHEN '503' THEN 'Institutional'
            END AS AccountType,
            AA.FullAddress,
            AA.StreetName,
            C.LastName,
            C.FirstName
        FROM [LogosDB].[dbo].[UtilityTransactionDetail] AS UTD
        JOIN UtilityAccount AS UA
            ON UTD.UtilityAccountID = UA.UtilityAccountID
        JOIN RateComponents AS RC
            ON RC.RateComponentID = UTD.RateComponentID
        JOIN RateProfile AS p
            ON p.RateProfileID = RC.RateProfileID
        JOIN RateProfileMaster AS m
            ON m.RateProfileMasterID = p.RateProfileMasterID
        JOIN PMCentralServiceAddress AS PMC
            ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
        JOIN Address AS AA
            ON AA.AddressID = PMC.AddressID
        JOIN UtilityCustomerAccount AS UCA
            ON UCA.UtilityAccountID = UA.UtilityAccountID
        LEFT JOIN UtilityCentralName AS UCN
            ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
        LEFT JOIN CentralName AS C
            ON C.CentralNameID = UCN.CentralNameID
        WHERE UTD.TransactionDate >= EOMONTH(DATEADD(DAY, -31, GETDATE()))
          AND UA.vsAccountType = '477'
    ),
    ExcludedAccounts AS (
        -- Identify accounts that should be excluded because they have a
        -- transaction in the last 60 days with a RateProfileMasterID of '12' or '119'
        SELECT DISTINCT
            UA.FullAccountNumber,
            CASE UA.vsAccountType
                WHEN '477' THEN 'Residential'
                WHEN '478' THEN 'Commercial'
                WHEN '479' THEN 'Industrial'
                WHEN '503' THEN 'Institutional'
            END AS AccountType,
            AA.FullAddress,
            AA.StreetName,
            C.LastName,
            C.FirstName
        FROM UtilityAccount AS UA
        JOIN UtilityCustomerAccount AS UCA
            ON UCA.UtilityAccountID = UA.UtilityAccountID
        JOIN PMCentralServiceAddress AS PMC
            ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
        JOIN Address AS AA
            ON AA.AddressID = PMC.AddressID
        LEFT JOIN UtilityCentralName AS UCN
            ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
        LEFT JOIN CentralName AS C
            ON C.CentralNameID = UCN.CentralNameID
        WHERE UA.AccountCloseDate IS NULL
          AND EXISTS (
              SELECT 1
              FROM [LogosDB].[dbo].[UtilityTransactionDetail] AS UTD
              JOIN RateComponents AS RC
                  ON RC.RateComponentID = UTD.RateComponentID
              JOIN RateProfile AS p
                  ON p.RateProfileID = RC.RateProfileID
              WHERE UTD.UtilityAccountID = UA.UtilityAccountID
                AND UTD.TransactionDate >= DATEADD(DAY, -60, GETDATE())
                AND p.RateProfileMasterID IN ('12', '119')
          )
    ),
    FilteredAccounts AS (
        -- Return records from BaseTransactions except those in ExcludedAccounts
        SELECT *
        FROM BaseTransactions
        EXCEPT
        SELECT *
        FROM ExcludedAccounts
    )
    -- Count accounts by street
    SELECT 
        StreetName,
        COUNT(*) AS AccountCount
    FROM FilteredAccounts
    GROUP BY StreetName
    ORDER BY COUNT(*) DESC, StreetName;
    """

    logger.info("Generated street summary query for accounts without garbage service")

    # No parameters for this query
    return query, ()
