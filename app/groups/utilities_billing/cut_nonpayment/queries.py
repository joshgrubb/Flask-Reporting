"""
Cut for Nonpayment SQL Queries.

This module contains the SQL queries used in the Cut for Nonpayment report.
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


def get_cut_nonpayment_accounts(cut_date=None, cycles=None):
    """
    Get accounts that have been cut for non-payment.

    Args:
        cut_date (datetime, optional): Date to start searching for cuts.
            If None, defaults to 30 days ago.
        cycles (list, optional): List of billing cycles to filter by.
            If None, all cycles are included.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default date if not provided
    if cut_date is None:
        cut_date = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0
        )

    # Format date for SQL
    cut_date_str = format_date_for_query(cut_date)

    # Start building parameters
    params = [cut_date_str]

    # Build cycle string and add to parameters if cycles is provided
    cycle_filter = "1=1"  # Default to all cycles
    if cycles and len(cycles) > 0:
        cycle_placeholders = ", ".join(["?"] * len(cycles))
        cycle_filter = f"VSR1.EntryValue IN ({cycle_placeholders})"
        params.extend(cycles)

    # Build the query with a parameterized cycle filter
    query = f"""
    WITH FilteredNotes
    AS (
        SELECT N.UsageKey,
            COUNT(DISTINCT N.NoteID) AS CUTS
        FROM Notes N
        WHERE N.CreatedDate >= ?
            AND N.Notes LIKE '%CUT FOR NONPAY%'
        GROUP BY N.UsageKey
        )
    SELECT DISTINCT UA.FullAccountNumber,
        LastName,
        FirstName,
        FullAddress,
        VSR1.EntryValue AS Cycle,
        VSE.EntryValue AS AccountType,
        FN.CUTS
    FROM dbo.UtilityAccount UA
    INNER JOIN dbo.UtilityAccountService UAS
        ON UAS.UtilityAccountID = UA.UtilityAccountID
    INNER JOIN dbo.UTAccountServiceMeter UASM
        ON UAS.UtilityAccountServiceID = UASM.UtilityAccountServiceID
    INNER JOIN dbo.CentralServiceAddressMeter CSAM
        ON UASM.CentralServiceAddressMeterID = CSAM.CentralServiceAddressMeterID
    INNER JOIN dbo.Services S
        ON S.ServiceID = UAS.ServiceID
    LEFT JOIN dbo.PMCentralServiceAddress PMC
        ON PMC.PMCentralServiceAddressID = UA.PMCentralServiceAddressID
    LEFT JOIN dbo.Address AD1
        ON Ad1.AddressID = PMC.AddressID
    LEFT JOIN dbo.UtilityCustomerAccount UCA
        ON UCA.UtilityAccountID = UA.UtilityAccountID
    LEFT JOIN dbo.UtilityCentralName UCN
        ON UCN.UtilityCentralNameID = UCA.UtilityCentralNameID
    LEFT JOIN dbo.CentralName CN
        ON CN.CentralNameID = UCN.CentralNameID
    LEFT JOIN dbo.ValidationSetEntry VSE
        ON VSE.EntryID = UA.vsAccountType
    LEFT JOIN dbo.ValidationSetEntry VSE1
        ON VSE1.EntryID = Ad1.vsState
    LEFT JOIN UT.enum_AccountServiceStatus() STAT
        ON UAS.ProcessStatus = STAT.AccountServiceStatus
    INNER JOIN FilteredNotes FN
        ON UA.UtilityAccountID = FN.UsageKey
    LEFT JOIN dbo.fn_UtilityAccountBillingProfile('99991231') UABP
        ON UA.UtilityAccountID = UABP.UtilityAccountID
            AND UABP.BillingProfileID IS NOT NULL
    INNER JOIN Routes R
        ON UABP.RouteID = R.RouteID
    INNER JOIN ValidationSetEntry VSR1
        ON R.RouteLevel1ID = VSR1.EntryID
    INNER JOIN ValidationSetEntry VSR2
        ON R.RouteLevel2ID = VSR2.EntryID
    WHERE UAS.ServiceEndDate IS NULL
        AND UA.AccountStatus IN (1) -- active accounts only
        AND STAT.AccountServiceStatusDescription IN ('Active') -- active services only
        AND CSAM.EndServiceDate IS NULL
        AND FN.CUTS > 0
        AND {cycle_filter}
    ORDER BY FN.CUTS DESC
    """

    logger.info(
        "Generated cut for nonpayment query with cut_date >= %s and cycles: %s",
        cut_date_str,
        str(cycles) if cycles else "All",
    )
    return query, tuple(params), "nws"


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


def get_cut_nonpayment_summary(cut_date=None, cycles=None):
    """
    Get summary data for cut for non-payment report.

    Args:
        cut_date (datetime, optional): Date to start searching for cuts.
            If None, defaults to 30 days ago.
        cycles (list, optional): List of billing cycles to filter by.
            If None, all cycles are included.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Use default date if not provided
    if cut_date is None:
        cut_date = (datetime.now() - timedelta(days=30)).replace(
            hour=0, minute=0, second=0
        )

    # Format date for SQL
    cut_date_str = format_date_for_query(cut_date)

    # Start building parameters
    params = [cut_date_str]

    # Build cycle string and add to parameters if cycles is provided
    cycle_filter = "1=1"  # Default to all cycles
    if cycles and len(cycles) > 0:
        cycle_placeholders = ", ".join(["?"] * len(cycles))
        cycle_filter = f"VSR1.EntryValue IN ({cycle_placeholders})"
        params.extend(cycles)

    # Build the query with a parameterized cycle filter
    query = f"""
    WITH FilteredNotes AS (
        SELECT N.UsageKey,
            COUNT(DISTINCT N.NoteID) AS CUTS
        FROM Notes N
        WHERE N.CreatedDate >= ?
            AND N.Notes LIKE '%CUT FOR NONPAY%'
        GROUP BY N.UsageKey
    ),
    CutAccountData AS (
        SELECT UA.FullAccountNumber,
            VSR1.EntryValue AS Cycle,
            VSE.EntryValue AS AccountType,
            FN.CUTS
        FROM dbo.UtilityAccount UA
        INNER JOIN dbo.UtilityAccountService UAS
            ON UAS.UtilityAccountID = UA.UtilityAccountID
        INNER JOIN dbo.UTAccountServiceMeter UASM
            ON UAS.UtilityAccountServiceID = UASM.UtilityAccountServiceID
        INNER JOIN dbo.CentralServiceAddressMeter CSAM
            ON UASM.CentralServiceAddressMeterID = CSAM.CentralServiceAddressMeterID
        INNER JOIN dbo.Services S
            ON S.ServiceID = UAS.ServiceID
        LEFT JOIN dbo.ValidationSetEntry VSE
            ON VSE.EntryID = UA.vsAccountType
        LEFT JOIN UT.enum_AccountServiceStatus() STAT
            ON UAS.ProcessStatus = STAT.AccountServiceStatus
        INNER JOIN FilteredNotes FN
            ON UA.UtilityAccountID = FN.UsageKey
        LEFT JOIN dbo.fn_UtilityAccountBillingProfile('99991231') UABP
            ON UA.UtilityAccountID = UABP.UtilityAccountID
                AND UABP.BillingProfileID IS NOT NULL
        INNER JOIN Routes R
            ON UABP.RouteID = R.RouteID
        INNER JOIN ValidationSetEntry VSR1
            ON R.RouteLevel1ID = VSR1.EntryID
        WHERE UAS.ServiceEndDate IS NULL
            AND UA.AccountStatus IN (1) -- active accounts only
            AND STAT.AccountServiceStatusDescription IN ('Active') -- active services only
            AND CSAM.EndServiceDate IS NULL
            AND FN.CUTS > 0
            AND {cycle_filter}
    )
    
    -- Summary data by cycle and account type
    SELECT 
        Cycle,
        AccountType,
        COUNT(*) AS AccountCount,
        SUM(CUTS) AS TotalCuts,
        AVG(CUTS) AS AvgCutsPerAccount,
        MAX(CUTS) AS MaxCutsPerAccount
    FROM CutAccountData
    GROUP BY Cycle, AccountType
    ORDER BY Cycle, AccountType
    """

    logger.info(
        "Generated cut for nonpayment summary query with cut_date >= %s and cycles: %s",
        cut_date_str,
        str(cycles) if cycles else "All",
    )
    return query, tuple(params), "nws"
