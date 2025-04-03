"""
Database connection module.

This module provides functionality for connecting to multiple SQL Server databases
using Windows Authentication and executing queries.
"""

import logging
import pyodbc
from flask import current_app, g

# Configure logger
logger = logging.getLogger(__name__)


def get_db_connection(db_key="nws"):
    """
    Get a database connection using Windows Authentication.

    Args:
        db_key (str): The key to identify which database to connect to.
            Options: "nws" (New World), "cw" (CityWorks).
            Defaults to "nws".

    Returns:
        pyodbc.Connection: A connection to the database.

    Raises:
        Exception: If connection fails.
    """
    # Create a unique connection key for g
    connection_key = f"db_conn_{db_key}"

    # Check if the connection already exists in g
    if not hasattr(g, connection_key):
        try:
            # Get configuration based on the requested database key
            if db_key == "nws":
                # New World database
                driver = current_app.config["NWS_DB_DRIVER"]
                server = current_app.config["NWS_DB_SERVER"]
                database = current_app.config["NWS_DB_NAME"]
                logger.info(
                    f"Connecting to New World database '{database}' on server '{server}'"
                )
            elif db_key == "cw":
                # CityWorks database
                driver = current_app.config["CW_DB_DRIVER"]
                server = current_app.config["CW_DB_SERVER"]
                database = current_app.config["CW_DB_NAME"]
                logger.info(
                    f"Connecting to CityWorks database '{database}' on server '{server}'"
                )
            else:
                logger.error(f"Unknown database key: {db_key}")
                raise ValueError(f"Unknown database key: {db_key}")

            # Build connection string for Windows Authentication
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )

            # Use setattr to set the connection on g
            setattr(g, connection_key, pyodbc.connect(conn_str))

        except Exception as e:
            logger.error(f"Database connection error for {db_key}: {str(e)}")
            raise

    # Use getattr to retrieve the connection from g
    return getattr(g, connection_key)


def close_db_connections(exception=None):
    """
    Close all database connections.

    Args:
        exception: An exception that might have occurred.
    """
    # Get all attributes of g object
    for key in list(vars(g)):
        # Check if the attribute is a database connection
        if key.startswith("db_conn_"):
            db_conn = getattr(g, key)
            if db_conn is not None:
                try:
                    db_conn.close()
                    logger.info(f"Database connection {key} closed")
                except Exception as e:
                    logger.error(f"Error closing database connection {key}: {str(e)}")

            # Remove the attribute from g
            delattr(g, key)


def execute_query(query, params=None, fetch_all=True, db_key="nws"):
    """
    Execute a SQL query and return the results.

    Args:
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for the query.
        fetch_all (bool, optional): Whether to fetch all results or just one.
            Defaults to True.
        db_key (str): The key to identify which database to connect to.
            Options: "nws" (New World), "cw" (CityWorks).
            Defaults to "nws".

    Returns:
        list or dict: The query results.

    Raises:
        Exception: If query execution fails.
    """
    conn = get_db_connection(db_key)
    cursor = None

    try:
        logger.info(f"Executing query on {db_key} database: {query}")
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
            logger.info(f"Query returned {len(results)} rows from {db_key} database")
            return results
        else:
            # Fetch just one row and convert to dict
            row = cursor.fetchone()
            if row:
                logger.info(f"Query returned 1 row from {db_key} database")
                return dict(zip(columns, row))
            else:
                logger.info(f"Query returned 0 rows from {db_key} database")
                return None

    except Exception as e:
        logger.error(f"Query execution error on {db_key} database: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
