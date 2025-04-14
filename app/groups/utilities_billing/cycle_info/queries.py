"""
Cycle Info SQL Queries.

This module contains the SQL queries used in the Cycle Info report.
Each function returns a SQL query string and optional parameters.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def get_available_cycles():
    """
    Get all available billing cycles.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT DISTINCT VSR1.EntryValue AS Cycle
    FROM dbo.Routes R
    INNER JOIN dbo.ValidationSetEntry VSR1
        ON R.RouteLevel1ID = VSR1.EntryID
    ORDER BY VSR1.EntryValue
    """

    logger.info("Getting available billing cycles")
    return query, (), "nws"


def get_cycle_info(cycles=None):
    """
    Get account information for specified billing cycles.

    Args:
        cycles (list, optional): List of billing cycles to filter by.
            If None, all cycles are included.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Build cycle filter
    cycle_filter = "1=1"  # Default to all cycles
    params = []

    if cycles and len(cycles) > 0:
        cycle_placeholders = ", ".join(["?"] * len(cycles))
        cycle_filter = f"VSR1.EntryValue IN ({cycle_placeholders})"
        params.extend(cycles)

    # Build the query
    query = f"""
    SELECT DISTINCT
        UA.FullAccountNumber,
        CN.FormalName,
        UCN.EmailAddress,
        AD.FullAddress,
        VSR1.EntryValue AS Cycle
    FROM dbo.UtilityAccount UA
    INNER JOIN dbo.UtilityCustomerAccount UCA
        ON UCA.UtilityAccountID = UA.UtilityAccountID
        AND UCA.PrimaryFlag = 1
    INNER JOIN dbo.UtilityCentralName UCN
        ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
    INNER JOIN dbo.CentralName CN
        ON CN.CentralNameID = UCN.CentralNameID
    LEFT JOIN dbo.PMCentralServiceAddress PMC
        ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
    LEFT JOIN dbo.Address AD
        ON AD.AddressID = PMC.AddressID
    LEFT JOIN dbo.fn_UtilityAccountBillingProfile('99991231') UABP
        ON UA.UtilityAccountID = UABP.UtilityAccountID
            AND UABP.BillingProfileID IS NOT NULL
    INNER JOIN Routes R
        ON UABP.RouteID = R.RouteID
    INNER JOIN ValidationSetEntry VSR1
        ON R.RouteLevel1ID = VSR1.EntryID
    WHERE UA.AccountStatus = 1  -- Active accounts only
        AND {cycle_filter}
        AND (
            UA.FullAccountNumber IS NOT NULL OR
            CN.FormalName IS NOT NULL OR
            UCN.EmailAddress IS NOT NULL OR
            AD.FullAddress IS NOT NULL
        )
    ORDER BY 
        UA.FullAccountNumber,
        CN.FormalName,
        UCN.EmailAddress,
        AD.FullAddress
    """

    logger.info(
        "Generated cycle info query with cycles: %s", str(cycles) if cycles else "All"
    )
    return query, tuple(params), "nws"


def get_cycle_summary():
    """
    Get summary statistics for each billing cycle.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT 
        VSR1.EntryValue AS Cycle,
        COUNT(DISTINCT UA.UtilityAccountID) AS AccountCount,
        COUNT(DISTINCT UCN.EmailAddress) AS EmailCount,
        SUM(CASE WHEN UCN.EmailAddress IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / 
            NULLIF(COUNT(*), 0) AS EmailPercentage
    FROM dbo.UtilityAccount UA
    INNER JOIN dbo.UtilityCustomerAccount UCA
        ON UCA.UtilityAccountID = UA.UtilityAccountID
        AND UCA.PrimaryFlag = 1
    INNER JOIN dbo.UtilityCentralName UCN
        ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
    LEFT JOIN dbo.fn_UtilityAccountBillingProfile('99991231') UABP
        ON UA.UtilityAccountID = UABP.UtilityAccountID
            AND UABP.BillingProfileID IS NOT NULL
    INNER JOIN Routes R
        ON UABP.RouteID = R.RouteID
    INNER JOIN ValidationSetEntry VSR1
        ON R.RouteLevel1ID = VSR1.EntryID
    WHERE UA.AccountStatus = 1  -- Active accounts only
    GROUP BY VSR1.EntryValue
    ORDER BY VSR1.EntryValue
    """

    logger.info("Generated cycle summary query")
    return query, (), "nws"
