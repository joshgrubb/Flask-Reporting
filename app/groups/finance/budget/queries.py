# budget_queries.py
"""
Budget Report SQL Queries.

This module contains SQL queries used in the Budget dashboard report.
"""

import logging
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)


def get_fiscal_years():
    """
    Get all available fiscal years for filtering.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    query = """
    SELECT DISTINCT Fiscal_Year 
    FROM vwGL_GLAccount_Monthly_Balances
    ORDER BY Fiscal_Year DESC
    """
    logger.info("Fetching available fiscal years")
    return query, (), "nws"


def get_fund_categories():
    """
    Get all available fund categories for filtering.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    query = """
    SELECT DISTINCT Fund_Category, Fund_Category_Sequence
    FROM vwGL_GLAccount_Full_View
    WHERE Fund_Category IS NOT NULL
    ORDER BY Fund_Category_Sequence
    """
    logger.info("Fetching available fund categories")
    return query, (), "nws"


def get_budget_summary(fiscal_year=None, fund_category=None):
    """
    Get budget summary data for the dashboard.

    Args:
        fiscal_year (str, optional): The fiscal year to filter by.
        fund_category (str, optional): The fund category to filter by.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Build WHERE clause based on parameters
    where_clauses = []
    params = []

    if fiscal_year:
        where_clauses.append("main.Fiscal_Year = ?")
        params.append(fiscal_year)

    if fund_category:
        where_clauses.append("fv.Fund_Category = ?")
        params.append(fund_category)

    where_sql = " AND ".join(where_clauses)
    where_sql = f"WHERE {where_sql}" if where_sql else ""

    query = f"""
    SELECT 
        fv.GL_Level_1_Description AS Fund,
        fv.GL_Level_2_Description AS Department,
        fv.GL_Level_3_Description AS Division,
        SUM(main.Budget) AS TotalBudget,
        SUM(main.Actual) AS TotalActual,
        SUM(main.Encumbrances) AS TotalEncumbrance,
        SUM(main.Budget - main.Actual - main.Encumbrances) AS RemainingBudget,
        CASE 
            WHEN SUM(main.Budget) <> 0 
            THEN (SUM(main.Actual) / SUM(main.Budget)) * 100 
            ELSE 0 
        END AS PercentSpent
    FROM 
        vwGL_GLAccount_Monthly_Balances main
    JOIN 
        vwGL_GLAccount_Full_View fv ON main.GL_Account_ID = fv.GL_Account_ID
    {where_sql}
    GROUP BY
        fv.GL_Level_1_Description,
        fv.GL_Level_2_Description,
        fv.GL_Level_3_Description
    ORDER BY
        fv.GL_Level_1_Description,
        fv.GL_Level_2_Description,
        fv.GL_Level_3_Description
    """

    logger.info("Fetching budget summary data with parameters: %s", params)
    return query, tuple(params), "nws"


def get_monthly_trend(fiscal_year=None, fund=None, department=None):
    """
    Get monthly budget and actual spending trends.

    Args:
        fiscal_year (str, optional): The fiscal year to filter by.
        fund (str, optional): The fund to filter by.
        department (str, optional): The department to filter by.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Build WHERE clause based on parameters
    where_clauses = []
    params = []

    if fiscal_year:
        where_clauses.append("main.Fiscal_Year = ?")
        params.append(fiscal_year)

    if fund:
        where_clauses.append("fv.GL_Level_1_Description = ?")
        params.append(fund)

    if department:
        where_clauses.append("fv.Department = ?")
        params.append(department)

    where_sql = " AND ".join(where_clauses)
    where_sql = f"WHERE {where_sql}" if where_sql else ""

    # Use the original SQL query structure but simplified for monthly trends
    query = f"""
    SELECT 
        main.Detail_Month AS Month,
        main.MonthNum,
        SUM(main.Actual) AS MonthlyActual,
        SUM(main.Budget) AS MonthlyBudget,
        SUM(main.RunningActual) AS RunningActual
    FROM 
        vwGL_GLAccount_Monthly_Balances main
    JOIN 
        vwGL_GLAccount_Full_View fv ON main.GL_Account_ID = fv.GL_Account_ID
    {where_sql}
    GROUP BY
        main.Detail_Month,
        main.MonthNum
    ORDER BY
        main.MonthNum
    """

    logger.info("Fetching monthly trend data with parameters: %s", params)
    return query, tuple(params), "nws"


def get_budget_transactions(fiscal_year=None, gl_account=None):
    """
    Get detailed budget transactions for a specific GL account.

    Args:
        fiscal_year (str, optional): The fiscal year to filter by.
        gl_account (str, optional): The GL account to filter by.

    Returns:
        tuple: (SQL query string, query parameters)
    """
    # Build WHERE clause based on parameters
    where_clauses = []
    params = []

    if fiscal_year:
        where_clauses.append("bt.Budget_Year = ?")
        params.append(fiscal_year)

    if gl_account:
        where_clauses.append("bt.GL_Account_Delimited = ?")
        params.append(gl_account)

    where_sql = " AND ".join(where_clauses)
    where_sql = f"WHERE {where_sql}" if where_sql else ""

    query = f"""
    SELECT 
        bt.GL_Account_Delimited,
        bt.Budget_Year,
        bt.Budget_Level,
        bt.Transaction_Description,
        bt.Units,
        bt.Amount_Per_Unit,
        bt.Total_Amount,
        bt.Last_Changed_Date,
        bt.Last_Changed_User
    FROM 
        vwAB_Budget_Transactions bt
    {where_sql}
    ORDER BY
        bt.Last_Changed_Date DESC
    """

    logger.info("Fetching budget transactions with parameters: %s", params)
    return query, tuple(params), "nws"
