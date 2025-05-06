# app/shared/work_order_details/queries.py
"""
Work Order Details SQL Queries.

This module contains the SQL queries for retrieving work order details.
"""

import logging

# Configure logger
logger = logging.getLogger(__name__)


def get_work_order_details(work_order_id):
    """
    Get detailed information for a specific work order.

    Args:
        work_order_id (str): The ID of the work order to retrieve.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Build the query for work order details
    query = """
    SELECT
        WORKORDERID,
        DESCRIPTION,
        SUPERVISOR,
        REQUESTEDBY,
        INITIATEDBY,
        INITIATEDATE,
        PROJECTNAME,
        LOCATION,
        PROJSTARTDATE,
        PROJFINISHDATE,
        ACTUALSTARTDATE,
        ACTUALFINISHDATE,
        WOCLOSEDBY,
        PRIORITY,
        SHOP,
        WOCATEGORY,
        WOCOST,
        WOLABORCOST,
        WOMATCOST,
        WOEQUIPCOST,
        STATUS,
        DATEWOCLOSED,
        WORKCOMPLETEDBY,
        WOADDRESS,
        STREETNAME,
        DISTRICT
    FROM CW.[azteca].WORKORDER
    WHERE WORKORDERID = ?
    """

    # Parameters
    params = [work_order_id]

    logger.info(
        "Generated work order details query for work order ID: %s", work_order_id
    )

    return query, tuple(params), "cw"


def get_work_order_comments(work_order_id):
    """
    Get all comments for a specific work order.

    Args:
        work_order_id (str): The ID of the work order to retrieve comments for.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Build the query for work order comments
    query = """
    SELECT
        WOC.WORKORDERID,
        WOC.AUTHORSID,
        E.EMPLOYEEID,
        E.LASTNAME,
        E.FIRSTNAME,
        WOC.COMMENTS,
        WOC.DATECREATED
    FROM CW.[azteca].WORKORDERCOMMENT AS WOC
    LEFT JOIN CW.[azteca].EMPLOYEE AS E
        ON WOC.AUTHORSID = E.EMPLOYEESID
    WHERE WOC.WORKORDERID = ?
    ORDER BY WOC.DATECREATED DESC
    """

    # Parameters
    params = [work_order_id]

    logger.info(
        "Generated work order comments query for work order ID: %s", work_order_id
    )

    return query, tuple(params), "cw"


def get_work_order_labor(work_order_id):
    """
    Get labor entries for a specific work order.

    Args:
        work_order_id (str): The ID of the work order to retrieve labor for.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    # Build the query for work order labor
    query = """
    SELECT
        CW.[azteca].LABORCOSTACT.WORKORDERID,
        CW.[azteca].LABORCOSTACT.LABORNAME,
        CW.[azteca].LABORCOSTACT.REGULARCOST,
        CW.[azteca].LABORCOSTACT.HOURS,
        CW.[azteca].LABORCOSTACT.TRANSDATE,
        CW.[azteca].WORKORDER.ACTUALSTARTDATE,
        CW.[azteca].WORKORDER.ACTUALFINISHDATE,
        CW.[azteca].WORKORDER.DESCRIPTION,
        CW.[azteca].WORKORDER.ISREACTIVE,
        CW.[azteca].WORKORDER.WOCATEGORY,
        CW.[azteca].LABORCOSTACT.LABORTYPE
    FROM CW.[azteca].LABORCOSTACT
        INNER JOIN
        CW.[azteca].WORKORDER
        ON CW.[azteca].LABORCOSTACT.WORKORDERID = CW.[azteca].WORKORDER.WORKORDERID
    WHERE CW.[azteca].LABORCOSTACT.WORKORDERID = ?
    ORDER BY CW.[azteca].WORKORDER.ACTUALFINISHDATE DESC
    """

    # Parameters
    params = [work_order_id]

    logger.info("Generated work order labor query for work order ID: %s", work_order_id)

    return query, tuple(params), "cw"
