#!/usr/bin/env python3
"""Test script to verify MySQL connection to local myapp1 database."""

import sys
import mysql.connector
from mysql.connector import Error


def test_mysql_connection():
    """Test connection to local MySQL myapp1 database."""
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            database='myapp1'
        )
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Successfully connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"✅ Connected to database: {record[0]}")
            
            # Test querying todos table
            cursor.execute("SELECT * FROM todos LIMIT 5;")
            rows = cursor.fetchall()
            print(f"✅ Successfully queried todos table, found {len(rows)} rows")
            
            # Show column names
            cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'myapp1' AND TABLE_NAME = 'todos';")
            columns = cursor.fetchall()
            print(f"✅ Todos table columns:")
            for col_name, col_type in columns:
                print(f"   - {col_name}: {col_type}")
            
            cursor.close()
            connection.close()
            print("✅ MySQL connection test passed!")
            return True
            
    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        return False


if __name__ == "__main__":
    success = test_mysql_connection()
    sys.exit(0 if success else 1)
