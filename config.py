"""Application configuration settings."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key-here"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database connection parameters
    DB_DRIVER = os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    DB_SERVER = os.environ.get("DB_SERVER", "localhost")
    DB_NAME = os.environ.get("DB_NAME", "master")
    DB_USERNAME = os.environ.get("DB_USERNAME", "sa")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "YourStrong!Passw0rd")

    # Cache configuration
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""

    DEBUG = True
    TESTING = True


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
