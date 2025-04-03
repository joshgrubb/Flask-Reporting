"""
Application configuration settings.

This module defines configuration classes for different environments.
Windows Authentication is used for SQL Server connections.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key-here"

    # New World database configuration (NWS)
    NWS_DB_DRIVER = os.environ.get("NWS_DB_DRIVER", "ODBC Driver 18 for SQL Server")
    NWS_DB_SERVER = os.environ.get("NWS_DB_SERVER", "toc-nwsdb-01")
    NWS_DB_NAME = os.environ.get("NWS_DB_NAME", "LogosDB")

    # CityWorks database configuration (CW)
    CW_DB_DRIVER = os.environ.get("CW_DB_DRIVER", "ODBC Driver 18 for SQL Server")
    CW_DB_SERVER = os.environ.get("CW_DB_SERVER", "TOC-CW-SVR-01")
    CW_DB_NAME = os.environ.get("CW_DB_NAME", "CW")

    # No username/password needed for Windows Authentication

    # Cache configuration
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True
    NWS_DB_NAME = os.environ.get("TEST_NWS_DB_NAME", "test_db")
    CW_DB_NAME = os.environ.get("TEST_CW_DB_NAME", "test_cw_db")


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Use more secure settings in production
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.environ.get("REDIS_URL")


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
