# queries.py
"""
Budget Report SQL Queries.

This module contains SQL queries used in the Budget dashboard report.
The queries use a custom SQL approach to match the view structure used in Power BI.
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
    # Instead of using the view directly, use the underlying query
    query = """
    SELECT DISTINCT Fiscal_Year 
    FROM (
        SELECT JD.FiscalEndYear AS Fiscal_Year
        FROM dbo.JournalHeader JH
        INNER JOIN dbo.JournalDetail JD ON JH.JournalID = JD.JournalID
        WHERE JH.ProcessStatus = 2 AND JD.GLDate IS NOT NULL
    ) AS YearData
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
        where_clauses.append(
            "cd.Fiscal_Year = ?"
        )  # Changed from main_data.Fiscal_Year to cd.Fiscal_Year
        params.append(fiscal_year)

    if fund_category:
        where_clauses.append("fv.Fund_Category = ?")
        params.append(fund_category)

    where_sql = " AND ".join(where_clauses)
    where_sql = f"WHERE {where_sql}" if where_sql else ""

    # Use the actual query structure from paste.txt but with correct referencing
    query = f"""
    WITH main_data AS (
        SELECT JD.GLAccountID AS GL_Account_ID,
            fnGLA.GLAccountDelimiter AS GL_Account_Delimited,
            JD.FiscalEndYear AS Fiscal_Year,
            YEAR(GLdate) AS Year,
            CASE MONTH(GLDate)
                WHEN 1 THEN 'January'
                WHEN 2 THEN 'February'
                WHEN 3 THEN 'March'
                WHEN 4 THEN 'April'
                WHEN 5 THEN 'May'
                WHEN 6 THEN 'June'
                WHEN 7 THEN 'July'
                WHEN 8 THEN 'August'
                WHEN 9 THEN 'September'
                WHEN 10 THEN 'October'
                WHEN 11 THEN 'November'
                WHEN 12 THEN 'December'
                END AS Detail_Month,
            MONTH(GLDate) AS MonthNum,
            SUM(CASE 
                    WHEN JH.JournalType = 1
                        THEN Amount
                    ELSE 0
                    END) AS Actual,
            SUM(CASE 
                    WHEN JH.JournalType = 3
                        THEN Amount
                    ELSE 0
                    END) AS Budget,
            SUM(CASE 
                    WHEN JH.JournalType = 4
                        THEN Amount
                    ELSE 0
                    END) AS Amendments,
            SUM(CASE 
                    WHEN JH.JournalType = 5
                        THEN Amount
                    ELSE 0
                    END) AS Encumbrances,
            CASE 
                WHEN MONTH(GLDate) = O1.FiscalStartMonth THEN 1
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 1 OR MONTH(GLDate) = O1.FiscalStartMonth + 1 - 12 THEN 2
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 2 OR MONTH(GLDate) = O1.FiscalStartMonth + 2 - 12 THEN 3
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 3 OR MONTH(GLDate) = O1.FiscalStartMonth + 3 - 12 THEN 4
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 4 OR MONTH(GLDate) = O1.FiscalStartMonth + 4 - 12 THEN 5
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 5 OR MONTH(GLDate) = O1.FiscalStartMonth + 5 - 12 THEN 6
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 6 OR MONTH(GLDate) = O1.FiscalStartMonth + 6 - 12 THEN 7
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 7 OR MONTH(GLDate) = O1.FiscalStartMonth + 7 - 12 THEN 8
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 8 OR MONTH(GLDate) = O1.FiscalStartMonth + 8 - 12 THEN 9
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 9 OR MONTH(GLDate) = O1.FiscalStartMonth + 9 - 12 THEN 10
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 10 OR MONTH(GLDate) = O1.FiscalStartMonth + 10 - 12 THEN 11
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 11 OR MONTH(GLDate) = O1.FiscalStartMonth + 11 - 12 THEN 12
                END AS Fiscal_Month,
            (
                SELECT ISNULL(SUM(Amount), 0)
                FROM JournalDetail JD1
                INNER JOIN JournalHeader JH1 ON JD1.JournalID = JH1.JournalID
                INNER JOIN GLAccount GLA1 ON JD1.GLAccountID = GLA1.GLAccountID
                INNER JOIN Account A1 ON GLA1.AccountID = A1.AccountID
                INNER JOIN Organization1 O2 ON GLA1.Org1ID = O2.OrganizationID
                WHERE JD1.GLAccountID = JD.GLAccountID AND JH1.ProcessStatus = 2 
                    AND JD1.GLDate IS NOT NULL AND JH1.JournalType = 1 
                    AND ((A1.AccountType IN (1, 2, 3) AND JD1.FiscalEndYear < JD.FiscalEndYear) 
                        OR (JD1.FiscalEndYear = JD.FiscalEndYear 
                            AND CASE 
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth THEN 1
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 1 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 1 - 12 THEN 2
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 2 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 2 - 12 THEN 3
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 3 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 3 - 12 THEN 4
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 4 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 4 - 12 THEN 5
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 5 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 5 - 12 THEN 6
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 6 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 6 - 12 THEN 7
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 7 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 7 - 12 THEN 8
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 8 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 8 - 12 THEN 9
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 9 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 9 - 12 THEN 10
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 10 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 10 - 12 THEN 11
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 11 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 11 - 12 THEN 12
                            END <= CASE 
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth THEN 1
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 1 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 1 - 12 THEN 2
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 2 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 2 - 12 THEN 3
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 3 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 3 - 12 THEN 4
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 4 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 4 - 12 THEN 5
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 5 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 5 - 12 THEN 6
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 6 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 6 - 12 THEN 7
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 7 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 7 - 12 THEN 8
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 8 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 8 - 12 THEN 9
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 9 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 9 - 12 THEN 10
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 10 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 10 - 12 THEN 11
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 11 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 11 - 12 THEN 12
                            END)
                    )
            ) AS RunningActual
        FROM dbo.JournalHeader JH
        INNER JOIN dbo.JournalDetail JD ON JH.JournalID = JD.JournalID
        LEFT JOIN dbo.fn_GLAccountWithDescription(NULL, NULL, NULL) fnGLA ON JD.GLAccountID = fnGLA.GLAccountID
        LEFT JOIN dbo.GLAccount GLA ON JD.GLAccountID = GLA.GLAccountID
        LEFT JOIN dbo.OrganizationSet OS ON GLA.OrgSetID = OS.OrgSetID
        LEFT JOIN dbo.Organization1 O1 ON OS.Org1 = O1.OrganizationID
        LEFT JOIN dbo.Account A ON GLA.AccountID = A.AccountID
        WHERE JH.ProcessStatus = 2 AND JD.GLDate IS NOT NULL
        GROUP BY JD.GLAccountID,
            fnGLA.GLAccountDelimiter,
            JD.FiscalEndYear,
            YEAR(GLdate),
            MONTH(GLdate),
            O1.FiscalStartMonth
    ),
    budget_totals AS (
        SELECT GL_Account_Delimited,
            Fiscal_Year,
            SUM(CASE 
                    WHEN Fiscal_Month = 1
                        THEN Budget
                    ELSE 0
                    END) AS TotalBudget
        FROM (
            SELECT fnGLA.GLAccountDelimiter AS GL_Account_Delimited,
                JD.FiscalEndYear AS Fiscal_Year,
                SUM(CASE 
                        WHEN JH.JournalType = 3
                            THEN Amount
                        ELSE 0
                        END) AS Budget,
                CASE 
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth THEN 1
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 1 OR MONTH(GLDate) = O1.FiscalStartMonth + 1 - 12 THEN 2
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 2 OR MONTH(GLDate) = O1.FiscalStartMonth + 2 - 12 THEN 3
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 3 OR MONTH(GLDate) = O1.FiscalStartMonth + 3 - 12 THEN 4
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 4 OR MONTH(GLDate) = O1.FiscalStartMonth + 4 - 12 THEN 5
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 5 OR MONTH(GLDate) = O1.FiscalStartMonth + 5 - 12 THEN 6
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 6 OR MONTH(GLDate) = O1.FiscalStartMonth + 6 - 12 THEN 7
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 7 OR MONTH(GLDate) = O1.FiscalStartMonth + 7 - 12 THEN 8
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 8 OR MONTH(GLDate) = O1.FiscalStartMonth + 8 - 12 THEN 9
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 9 OR MONTH(GLDate) = O1.FiscalStartMonth + 9 - 12 THEN 10
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 10 OR MONTH(GLDate) = O1.FiscalStartMonth + 10 - 12 THEN 11
                    WHEN MONTH(GLDate) = O1.FiscalStartMonth + 11 OR MONTH(GLDate) = O1.FiscalStartMonth + 11 - 12 THEN 12
                    END AS Fiscal_Month
            FROM dbo.JournalHeader JH
            INNER JOIN dbo.JournalDetail JD ON JH.JournalID = JD.JournalID
            LEFT JOIN dbo.fn_GLAccountWithDescription(NULL, NULL, NULL) fnGLA ON JD.GLAccountID = fnGLA.GLAccountID
            LEFT JOIN dbo.GLAccount GLA ON JD.GLAccountID = GLA.GLAccountID
            LEFT JOIN dbo.OrganizationSet OS ON GLA.OrgSetID = OS.OrgSetID
            LEFT JOIN dbo.Organization1 O1 ON OS.Org1 = O1.OrganizationID
            WHERE JH.ProcessStatus = 2 AND JD.GLDate IS NOT NULL
            GROUP BY fnGLA.GLAccountDelimiter,
                JD.FiscalEndYear,
                MONTH(GLdate),
                O1.FiscalStartMonth
            ) AS budget_subquery
        GROUP BY GL_Account_Delimited,
            Fiscal_Year
    ),
    combined_data AS (
        SELECT
            main_data.GL_Account_ID,
            main_data.GL_Account_Delimited,
            main_data.Fiscal_Year,
            main_data.Year,
            main_data.Detail_Month,
            main_data.MonthNum,
            main_data.Actual,
            budget_totals.TotalBudget AS Budget,
            main_data.Amendments,
            main_data.Encumbrances,
            main_data.Fiscal_Month,
            main_data.RunningActual
        FROM main_data
        INNER JOIN budget_totals ON
            main_data.GL_Account_Delimited = budget_totals.GL_Account_Delimited
            AND main_data.Fiscal_Year = budget_totals.Fiscal_Year
    )
    SELECT
        fv.GL_Level_1_Description AS Fund,
        fv.GL_Level_2_Description AS Department,
        fv.GL_Level_3_Description AS Division,
        SUM(cd.Budget) AS TotalBudget,
        SUM(cd.Actual) AS TotalActual,
        SUM(cd.Encumbrances) AS TotalEncumbrance,
        SUM(cd.Budget - cd.Actual - cd.Encumbrances) AS RemainingBudget,
        CASE
            WHEN SUM(cd.Budget) <> 0
            THEN (SUM(cd.Actual) / SUM(cd.Budget)) * 100
            ELSE 0
        END AS PercentSpent
    FROM
        combined_data cd
    JOIN
        vwGL_GLAccount_Full_View fv ON cd.GL_Account_ID = fv.GL_Account_ID
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
        where_clauses.append("main_data.Fiscal_Year = ?")
        params.append(fiscal_year)

    if fund:
        where_clauses.append("fv.GL_Level_1_Description = ?")
        params.append(fund)

    if department:
        where_clauses.append("fv.Department = ?")
        params.append(department)

    where_sql = " AND ".join(where_clauses)
    where_sql = f"WHERE {where_sql}" if where_sql else ""

    # Use the actual query structure from paste.txt but tailored for monthly trends
    query = f"""
    WITH main_data AS (
        SELECT JD.GLAccountID AS GL_Account_ID,
            fnGLA.GLAccountDelimiter AS GL_Account_Delimited,
            JD.FiscalEndYear AS Fiscal_Year,
            YEAR(GLdate) AS Year,
            CASE MONTH(GLDate)
                WHEN 1 THEN 'January'
                WHEN 2 THEN 'February'
                WHEN 3 THEN 'March'
                WHEN 4 THEN 'April'
                WHEN 5 THEN 'May'
                WHEN 6 THEN 'June'
                WHEN 7 THEN 'July'
                WHEN 8 THEN 'August'
                WHEN 9 THEN 'September'
                WHEN 10 THEN 'October'
                WHEN 11 THEN 'November'
                WHEN 12 THEN 'December'
                END AS Detail_Month,
            MONTH(GLDate) AS MonthNum,
            SUM(CASE 
                    WHEN JH.JournalType = 1
                        THEN Amount
                    ELSE 0
                    END) AS Actual,
            SUM(CASE 
                    WHEN JH.JournalType = 3
                        THEN Amount
                    ELSE 0
                    END) AS Budget,
            SUM(CASE 
                    WHEN JH.JournalType = 4
                        THEN Amount
                    ELSE 0
                    END) AS Amendments,
            SUM(CASE 
                    WHEN JH.JournalType = 5
                        THEN Amount
                    ELSE 0
                    END) AS Encumbrances,
            CASE 
                WHEN MONTH(GLDate) = O1.FiscalStartMonth THEN 1
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 1 OR MONTH(GLDate) = O1.FiscalStartMonth + 1 - 12 THEN 2
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 2 OR MONTH(GLDate) = O1.FiscalStartMonth + 2 - 12 THEN 3
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 3 OR MONTH(GLDate) = O1.FiscalStartMonth + 3 - 12 THEN 4
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 4 OR MONTH(GLDate) = O1.FiscalStartMonth + 4 - 12 THEN 5
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 5 OR MONTH(GLDate) = O1.FiscalStartMonth + 5 - 12 THEN 6
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 6 OR MONTH(GLDate) = O1.FiscalStartMonth + 6 - 12 THEN 7
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 7 OR MONTH(GLDate) = O1.FiscalStartMonth + 7 - 12 THEN 8
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 8 OR MONTH(GLDate) = O1.FiscalStartMonth + 8 - 12 THEN 9
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 9 OR MONTH(GLDate) = O1.FiscalStartMonth + 9 - 12 THEN 10
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 10 OR MONTH(GLDate) = O1.FiscalStartMonth + 10 - 12 THEN 11
                WHEN MONTH(GLDate) = O1.FiscalStartMonth + 11 OR MONTH(GLDate) = O1.FiscalStartMonth + 11 - 12 THEN 12
                END AS Fiscal_Month,
            (
                SELECT ISNULL(SUM(Amount), 0)
                FROM JournalDetail JD1
                INNER JOIN JournalHeader JH1 ON JD1.JournalID = JH1.JournalID
                INNER JOIN GLAccount GLA1 ON JD1.GLAccountID = GLA1.GLAccountID
                INNER JOIN Account A1 ON GLA1.AccountID = A1.AccountID
                INNER JOIN Organization1 O2 ON GLA1.Org1ID = O2.OrganizationID
                WHERE JD1.GLAccountID = JD.GLAccountID AND JH1.ProcessStatus = 2 
                    AND JD1.GLDate IS NOT NULL AND JH1.JournalType = 1 
                    AND ((A1.AccountType IN (1, 2, 3) AND JD1.FiscalEndYear < JD.FiscalEndYear) 
                        OR (JD1.FiscalEndYear = JD.FiscalEndYear 
                            AND CASE 
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth THEN 1
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 1 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 1 - 12 THEN 2
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 2 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 2 - 12 THEN 3
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 3 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 3 - 12 THEN 4
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 4 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 4 - 12 THEN 5
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 5 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 5 - 12 THEN 6
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 6 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 6 - 12 THEN 7
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 7 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 7 - 12 THEN 8
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 8 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 8 - 12 THEN 9
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 9 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 9 - 12 THEN 10
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 10 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 10 - 12 THEN 11
                                WHEN MONTH(JD1.GLDate) = O2.FiscalStartMonth + 11 OR MONTH(JD1.GLDate) = O2.FiscalStartMonth + 11 - 12 THEN 12
                            END <= CASE 
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth THEN 1
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 1 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 1 - 12 THEN 2
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 2 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 2 - 12 THEN 3
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 3 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 3 - 12 THEN 4
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 4 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 4 - 12 THEN 5
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 5 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 5 - 12 THEN 6
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 6 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 6 - 12 THEN 7
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 7 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 7 - 12 THEN 8
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 8 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 8 - 12 THEN 9
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 9 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 9 - 12 THEN 10
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 10 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 10 - 12 THEN 11
                                WHEN MONTH(JD.GLDate) = O1.FiscalStartMonth + 11 OR MONTH(JD.GLDate) = O1.FiscalStartMonth + 11 - 12 THEN 12
                            END)
                    )
            ) AS RunningActual
        FROM dbo.JournalHeader JH
        INNER JOIN dbo.JournalDetail JD ON JH.JournalID = JD.JournalID
        LEFT JOIN dbo.fn_GLAccountWithDescription(NULL, NULL, NULL) fnGLA ON JD.GLAccountID = fnGLA.GLAccountID
        LEFT JOIN dbo.GLAccount GLA ON JD.GLAccountID = GLA.GLAccountID
        LEFT JOIN dbo.OrganizationSet OS ON GLA.OrgSetID = OS.OrgSetID
        LEFT JOIN dbo.Organization1 O1 ON OS.Org1 = O1.OrganizationID
        LEFT JOIN dbo.Account A ON GLA.AccountID = A.AccountID
        WHERE JH.ProcessStatus = 2 AND JD.GLDate IS NOT NULL
        GROUP BY JD.GLAccountID,
            fnGLA.GLAccountDelimiter,
            JD.FiscalEndYear,
            YEAR(GLdate),
            MONTH(GLdate),
            O1.FiscalStartMonth
    )
    SELECT 
        main_data.Detail_Month AS Month,
        main_data.MonthNum,
        SUM(main_data.Actual) AS MonthlyActual,
        SUM(main_data.Budget) AS MonthlyBudget,
        SUM(main_data.RunningActual) AS RunningActual
    FROM 
        main_data
    JOIN 
        vwGL_GLAccount_Full_View fv ON main_data.GL_Account_ID = fv.GL_Account_ID
    {where_sql}
    GROUP BY
        main_data.Detail_Month,
        main_data.MonthNum
    ORDER BY
        main_data.MonthNum
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


def get_amended_budget_by_fiscal_year(fiscal_year=None, department=None):
    """
    Get amended budget totals grouped by fiscal year with optimizations.
    Only selects necessary columns and uses better filtering.

    Args:
        fiscal_year (str, optional): A specific fiscal year to filter by.
        department (str, optional): A specific department to filter by.

    Returns:
        tuple: (SQL query string, query parameters, database key)
    """
    where_clauses = []
    params = []

    # Ensure only valid parameters are included
    if fiscal_year and str(fiscal_year).lower() not in ("none", ""):
        where_clauses.append("JD.FiscalEndYear = ?")
        params.append(fiscal_year)

    if department and str(department).lower() not in ("none", ""):
        where_clauses.append("fv.GL_Level_2_Description = ?")
        params.append(department)

    where_sql = ""
    if where_clauses:
        # Prepend "AND" since our WHERE clause already includes mandatory conditions.
        where_sql = " AND " + " AND ".join(where_clauses)

    # Optimized query with NOLOCK hint to improve performance
    query = f"""
    SELECT JD.FiscalEndYear AS Fiscal_Year,
           SUM(
               CASE WHEN JH.JournalType = 3 THEN Amount ELSE 0 END +
               CASE WHEN JH.JournalType = 4 THEN Amount ELSE 0 END
           ) AS AmendedBudget
    FROM dbo.JournalHeader JH WITH (NOLOCK)
    INNER JOIN dbo.JournalDetail JD WITH (NOLOCK) ON JH.JournalID = JD.JournalID
    LEFT JOIN vwGL_GLAccount_Full_View fv WITH (NOLOCK) ON fv.GL_Account_ID = JD.GLAccountID
    WHERE JH.ProcessStatus = 2 AND JD.GLDate IS NOT NULL
    {where_sql}
    GROUP BY JD.FiscalEndYear
    ORDER BY JD.FiscalEndYear
    """

    logger.debug("Executing query with params: %s", params)
    return query, tuple(params), "nws"
