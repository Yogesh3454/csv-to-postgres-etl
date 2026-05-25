"""
db.py - PostgreSQL Connection Utility
Handles creating and closing database connections using psycopg2.
"""

import os
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv
from scripts.logger import setup_logger

# Load environment variables from config/.env
load_dotenv(dotenv_path="config/.env")

logger = setup_logger()


def get_connection() -> connection:
    """
    Create and return a PostgreSQL connection using env variables.

    Returns:
        psycopg2 connection object.

    Raises:
        Exception: If connection fails.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            dbname=os.getenv("DB_NAME", "etl_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "yoggunjal123"),
        )
        logger.info("Database connection established.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def close_connection(conn: connection) -> None:
    """Safely close a database connection."""
    if conn and not conn.closed:
        conn.close()
        logger.info("Database connection closed.")
