"""
Sample query test script.

This script tests executing a specific query with parameters.
Modify the query to match your database schema and reporting needs.
"""

import sys
import logging
from flask import Flask
from app.core.database import execute_query
from config import DevelopmentConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_sample_query():
    """Test a sample query with parameters."""
    # Create a minimal Flask app with config
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    with app.app_context():
        try:
            # Example: Query with parameters
            # Replace this with a query relevant to your actual database schema
            query = """
            SELECT TOP 10 *
            FROM sys.tables
            WHERE name LIKE ?
            ORDER BY name
            """

            # Parameter for the query (account numbers starting with '1')
            params = ("A%",)

            logger.info("Executing sample query with parameters...")
            results = execute_query(query, params)

            # Display results
            if results:
                logger.info(f"Query returned {len(results)} results:")
                for i, row in enumerate(results, 1):
                    # Print the first few fields of each row
                    # Adjust these field names to match your actual query
                    logger.info(f"  {i}. Table: {row.get('name', 'N/A')}")
            else:
                logger.info("Query returned no results.")

            return True

        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            return False


if __name__ == "__main__":
    logger.info("Testing sample query...")
    success = test_sample_query()

    if success:
        logger.info("Query test passed successfully!")
        sys.exit(0)
    else:
        logger.error("Query test failed.")
        sys.exit(1)
