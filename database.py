"""
Database Connection Module
Handles all MySQL database connections and queries
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """
    Execute a SQL query

    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch: If True, return results; if False, commit changes

    Returns:
        Results if fetch=True, else number of affected rows
    """
    connection = get_db_connection()

    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())

        if fetch:
            result = cursor.fetchall()
            cursor.close()
            connection.close()
            return result

        else:
            connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            connection.close()
            return affected_rows

    except Error as e:
        print(f"Query execution error: {e}")

        if connection:
            connection.close()

        return None

def execute_single(query, params=None):
    """Execute query and return single row"""

    connection = get_db_connection()

    if not connection:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result

    except Error as e:
        print(f"Query execution error: {e}")

        if connection:
            connection.close()

        return None