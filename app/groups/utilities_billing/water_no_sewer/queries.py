"""
Water No Sewer SQL Queries.

This module contains the SQL queries used in the Water No Sewer report.
Each function returns a SQL query string and optional parameters.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def get_water_no_sewer_accounts():
    """
    Get accounts that have water service but no sewer service.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT UA.FullAccountNumber,
        VSE.EntryValue AS AccountType,
        CN.LastName,
        CN.FirstName
    FROM dbo.UtilityAccount UA
    INNER JOIN dbo.UtilityAccountService UAS
        ON UA.UtilityAccountID = UAS.UtilityAccountID
    INNER JOIN dbo.UTConsumptionHeader H
        ON UA.UtilityAccountID = H.UtilityAccountID
    -- Retrieve meter rates if available
    LEFT JOIN dbo.CentralServiceMeterRates CSMR
        ON CSMR.CentralServiceAddressMeterID = H.CentralServiceAddressMeterID
    INNER JOIN RateProfileMaster RM
        ON CSMR.RateProfileMasterID = RM.RateProfileMasterID
    INNER JOIN ServiceClass SC
        ON RM.ServiceClassID = SC.ServiceClassID
    INNER JOIN dbo.Services S
        ON S.ServiceID = UAS.ServiceID
    -- Ensure valid customer account info exists
    INNER JOIN dbo.UtilityCustomerAccount UCA
        ON UCA.UtilityAccountID = UA.UtilityAccountID
    LEFT JOIN dbo.UtilityCentralName UCN
        ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
    LEFT JOIN dbo.CentralName CN
        ON CN.CentralNameID = UCN.CentralNameID
    LEFT JOIN dbo.ValidationSetEntry VSE
        ON VSE.EntryID = UA.vsAccountType
    INNER JOIN RateProfile RP
        ON RM.RateProfileMasterID = RP.RateProfileMasterID
    INNER JOIN RateComponents RC
        ON RP.RateProfileID = RC.RateProfileID
    WHERE
        -- Ensure the service is Water & Sewer (exact match used; switch back to LIKE if partial match is needed)
        S.ServiceDescription = 'Water & Sewer'
        AND SC.ServiceClassDescription = 'Water & Sewer'
        -- Only active water services (date and flag filtering)
        AND UAS.ServiceEndDate IS NULL
        AND H.MeterReadDate >= DATEADD(day, - 40, GETDATE())
        AND CSMR.EffectiveEndDate > GETDATE() -- eliminates inactive meters
        AND UCA.PrimaryFlag = 1
        AND UA.AccountStatus = 1 -- active accounts only
        AND RM.RateProfileActiveFlag = 1 -- active rate profiles only
        AND RP.RateProfileEED >= GETDATE()
        AND RM.InactiveDate IS NULL
    GROUP BY UA.FullAccountNumber,
        VSE.EntryValue,
        CN.LastName,
        CN.FirstName
    HAVING
        -- Include only groups with at least one Water rate profile and no Sewer rate profile
        COUNT(CASE
                WHEN RM.RateProfileDescription LIKE '%Water%'
                    THEN 1
                END) > 0
        AND COUNT(CASE
                WHEN RM.RateProfileDescription LIKE '%Sewer%'
                    THEN 1
                END) = 0
    ORDER BY UA.FullAccountNumber DESC
    """

    logger.info("Generated water no sewer accounts query")
    return query, (), "nws"


def get_account_type_summary():
    """
    Get summary statistics for accounts by account type.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Simplified query that just summarizes the accounts from the main query
    query = """
    WITH AccountsWithWaterNoSewer AS (
        SELECT UA.FullAccountNumber,
            VSE.EntryValue AS AccountType,
            CN.LastName,
            CN.FirstName
        FROM dbo.UtilityAccount UA
        INNER JOIN dbo.UtilityAccountService UAS
            ON UA.UtilityAccountID = UAS.UtilityAccountID
        INNER JOIN dbo.UTConsumptionHeader H
            ON UA.UtilityAccountID = H.UtilityAccountID
        LEFT JOIN dbo.CentralServiceMeterRates CSMR
            ON CSMR.CentralServiceAddressMeterID = H.CentralServiceAddressMeterID
        INNER JOIN RateProfileMaster RM
            ON CSMR.RateProfileMasterID = RM.RateProfileMasterID
        INNER JOIN ServiceClass SC
            ON RM.ServiceClassID = SC.ServiceClassID
        INNER JOIN dbo.Services S
            ON S.ServiceID = UAS.ServiceID
        INNER JOIN dbo.UtilityCustomerAccount UCA
            ON UCA.UtilityAccountID = UA.UtilityAccountID
        LEFT JOIN dbo.UtilityCentralName UCN
            ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
        LEFT JOIN dbo.CentralName CN
            ON CN.CentralNameID = UCN.CentralNameID
        LEFT JOIN dbo.ValidationSetEntry VSE
            ON VSE.EntryID = UA.vsAccountType
        INNER JOIN RateProfile RP
            ON RM.RateProfileMasterID = RP.RateProfileMasterID
        INNER JOIN RateComponents RC
            ON RP.RateProfileID = RC.RateProfileID
        WHERE
            S.ServiceDescription = 'Water & Sewer'
            AND SC.ServiceClassDescription = 'Water & Sewer'
            AND UAS.ServiceEndDate IS NULL
            AND H.MeterReadDate >= DATEADD(day, - 40, GETDATE())
            AND CSMR.EffectiveEndDate > GETDATE()
            AND UCA.PrimaryFlag = 1
            AND UA.AccountStatus = 1
            AND RM.RateProfileActiveFlag = 1
            AND RP.RateProfileEED >= GETDATE()
            AND RM.InactiveDate IS NULL
        GROUP BY UA.FullAccountNumber,
            VSE.EntryValue,
            CN.LastName,
            CN.FirstName
        HAVING
            COUNT(CASE
                    WHEN RM.RateProfileDescription LIKE '%Water%'
                        THEN 1
                    END) > 0
            AND COUNT(CASE
                    WHEN RM.RateProfileDescription LIKE '%Sewer%'
                        THEN 1
                    END) = 0
    )
    SELECT 
        ISNULL(AccountType, 'Unknown') AS AccountType,
        COUNT(*) AS AccountCount
    FROM AccountsWithWaterNoSewer
    GROUP BY AccountType
    ORDER BY COUNT(*) DESC
    """

    logger.info("Generated account type summary query for water no sewer accounts")
    return query, (), "nws"
