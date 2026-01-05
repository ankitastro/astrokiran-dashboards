"""
Database functions - all stateless, under 20 lines each.
"""

import os
import time
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_ENDPOINT'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': 'astrokiran',
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD')
}

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


def get_connection():
    """Create a new database connection with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise


def execute_query(query: str, params: tuple = None) -> list:
    """Execute a query and return all results with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except psycopg2.OperationalError:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
            else:
                raise


def execute_single(query: str, params: tuple = None):
    """Execute a query and return single row."""
    results = execute_query(query, params)
    return results[0] if results else None


def execute_scalar(query: str, params: tuple = None):
    """Execute a query and return single value."""
    row = execute_single(query, params)
    return row[0] if row else None
