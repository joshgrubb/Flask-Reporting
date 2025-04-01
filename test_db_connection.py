"""
Database connection test script.

This script tests the database connection and executes a sample query.
Run this script directly to test database connectivity.
"""

import sys
import logging
from flask import Flask
from app.core.database import get_db_connection, execute_query
from config import DevelopmentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test database connection and run a sample query."""
    # Create a minimal Flask app with config
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    with app.app_context():
        try:
            # Test connection
            logger.info("Testing database connection...")
            conn = get_db_connection()
            logger.info("Connection successful!")

            # Test query - get first 5 tables in the database
            query = """
            SELECT TOP 5 
                t.name AS table_name,
                s.name AS schema_name
            FROM 
                sys.tables t
            INNER JOIN 
                sys.schemas s ON t.schema_id = s.schema_id
            ORDER BY 
                s.name, t.name
            """

            logger.info("Executing test query to list tables...")
            results = execute_query(query)

            # Display results
            if results:
                logger.info("Query successful! Tables found:")
                for i, table in enumerate(results, 1):
                    logger.info(f"  {i}. {table['schema_name']}.{table['table_name']}")
            else:
                logger.info("Query returned no results.")

            return True

        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            return False


if __name__ == "__main__":
    logger.info("Starting database connection test...")
    success = test_connection()

    if success:
        logger.info("All tests passed successfully!")
        sys.exit(0)
    else:
        logger.error("Tests failed.")
        sys.exit(1)
