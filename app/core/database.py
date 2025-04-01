"""
Database connection module.

This module provides functionality for connecting to the SQL Server database
using Windows Authentication and executing queries.
"""

import logging
import pyodbc
from flask import current_app, g

# Configure logger
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Get a database connection using Windows Authentication.

    Returns:
        pyodbc.Connection: A connection to the database.

    Raises:
        Exception: If connection fails.
    """
    if "db_conn" not in g:
        try:
            # Get configuration from current app
            driver = current_app.config["DB_DRIVER"]
            server = current_app.config["DB_SERVER"]
            database = current_app.config["DB_NAME"]

            # Build connection string for Windows Authentication
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )

            logger.info(f"Connecting to database '{database}' on server '{server}'")
            g.db_conn = pyodbc.connect(conn_str)

        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    return g.db_conn


def close_db_connection(exception=None):
    """
    Close the database connection.

    Args:
        exception: An exception that might have occurred.
    """
    db_conn = g.pop("db_conn", None)

    if db_conn is not None:
        try:
            db_conn.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}")


def execute_query(query, params=None, fetch_all=True):
    """
    Execute a SQL query and return the results.

    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for the query.
        fetch_all (bool, optional): Whether to fetch all results or just one.
            Defaults to True.

    Returns:
        list or dict: The query results.

    Raises:
        Exception: If query execution fails.
    """
    conn = get_db_connection()
    cursor = None

    try:
        logger.info(f"Executing query: {query}")
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Get column names
        columns = [column[0] for column in cursor.description]

        if fetch_all:
            # Fetch all results and convert to list of dicts
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            logger.info(f"Query returned {len(results)} rows")
            return results
        else:
            # Fetch just one row and convert to dict
            row = cursor.fetchone()
            if row:
                logger.info("Query returned 1 row")
                return dict(zip(columns, row))
            else:
                logger.info("Query returned 0 rows")
                return None

    except Exception as e:
        logger.error(f"Query execution error: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
