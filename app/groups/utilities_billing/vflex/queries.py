# app/groups/utilities_billing/vflex/queries.py
"""
VFLEX SQL Queries.

This module contains the SQL queries used in the VFLEX report,
primarily calling the sp_VFLEX_Export stored procedure.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def get_vflex_data():
    """
    Get the VFLEX export data by calling the sp_VFLEX_Export stored procedure.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Call the stored procedure
    query = "EXEC [dbo].[sp_VFLEX_Export]"

    logger.info("Generating VFLEX export data using sp_VFLEX_Export")
    return query, (), "nws"


def get_vflex_error_log(limit=100):
    """
    Get the recent error logs for the VFLEX export process.

    Args:
        limit (int): Maximum number of log entries to retrieve.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT TOP (?)
        [ErrorID],
        [Status],
        [ErrorMessage],
        [ErrorSeverity],
        [ErrorState],
        [ErrorProcedure],
        [ExecutionSeconds],
        [ErrorTime]
    FROM [dbo].[VFLEX_ErrorLog]
    ORDER BY [ErrorTime] DESC
    """

    logger.info("Retrieving VFLEX error logs, limit: %d", limit)
    return query, (limit,), "nws"


def get_execution_stats():
    """
    Get statistics about the VFLEX export process.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    query = """
    SELECT 
        COUNT(*) AS TotalExecutions,
        SUM(CASE WHEN [Status] = 'Success' THEN 1 ELSE 0 END) AS SuccessfulExecutions,
        SUM(CASE WHEN [Status] = 'Error' THEN 1 ELSE 0 END) AS FailedExecutions,
        AVG(ExecutionSeconds) AS AvgExecutionTime,
        MAX(ExecutionSeconds) AS MaxExecutionTime,
        MIN(CASE WHEN [Status] = 'Success' THEN ExecutionSeconds ELSE NULL END) AS MinExecutionTime,
        MAX(ErrorTime) AS LastExecution
    FROM [dbo].[VFLEX_ErrorLog]
    """

    logger.info("Retrieving VFLEX execution statistics")
    return query, (), "nws"


def get_vflex_record_count():
    """
    Get the number of records that would be exported by the VFLEX process.
    This uses a count of MeterID values from the relevant tables instead of
    executing the full stored procedure.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Simplified version of the query that counts records without executing the full procedure
    query = """
    SELECT COUNT(DISTINCT CSM.MeterID) AS RecordCount
    FROM dbo.UtilityAccount UA WITH (nolock)
    INNER JOIN dbo.UtilityCustomerAccount UCA WITH (nolock)
        ON UCA.UtilityAccountID = UA.UtilityAccountID
        AND UCA.PrimaryFlag = 1
        AND UCA.CustomerAccountEndDate IS NULL
    INNER JOIN dbo.UtilityAccountService UAS WITH (nolock)
        ON UAS.UtilityAccountID = UA.UtilityAccountID
    INNER JOIN dbo.UTAccountServiceMeter ASM WITH (nolock)
        ON ASM.UtilityAccountServiceID = UAS.UtilityAccountServiceID
    INNER JOIN dbo.CentralServiceAddressMeter CSM WITH (nolock)
        ON CSM.CentralServiceAddressMeterID = ASM.CentralServiceAddressMeterID
        AND CSM.MeterID = ASM.MeterID
    LEFT JOIN UT.CentralServiceAddressMeterMeasurementOverrides utcsmo WITH (nolock)
        ON utcsmo.CentralServiceAddressMeterID = csm.CentralServiceAddressMeterID
    LEFT JOIN UT.MeterGroupParts MGP WITH (nolock)
        ON MGP.MeterGroupId = CSM.MeterGroupId
    LEFT JOIN UT.Parts PRT WITH (nolock)
        ON PRT.PartId = MGP.PartId
    LEFT JOIN UT.PartTypes TYP WITH (nolock)
        ON TYP.PartTypeId = PRT.PartTypeId
    LEFT JOIN ut.PartTypeUDFs upud WITH (nolock)
        ON upud.parttypeid = typ.parttypeid
        AND upud.attributeid = 127
    LEFT JOIN ut.PartUserDefined pud WITH (nolock)
        ON pud.partid = prt.partid
        AND upud.attributeid = 127
    WHERE (
        (CSM.EndServiceDate IS NULL
        AND utcsmo.AMRDeviceCode = 'AMI'
        AND UA.AccountStatus = 1
        AND ISNULL(pud.attributevalue, '') <> 'true')
        OR
        (PRT.PartNumber IN ('KZG030886107', 'KZG030886146')
        AND utcsmo.ServiceMultiplier <> 1.0000000)
    )
    AND UTCSMO.AMRNumber NOT IN ('94650356', '94515458', '94520920', '98307852')
    """

    logger.info("Counting VFLEX records that will be exported")
    return query, (), "nws"
