"""SQL query execution service for PostgreSQL and MySQL."""

import time
from datetime import datetime, date
from decimal import Decimal
from typing import Any

from src.models.query import QueryResult
from src.services.db_connection import db_connection_service
from src.utils.sql_validator import sql_validator


class QueryExecutorService:
    """Service for executing SQL queries."""

    def execute_query(self, url: str, sql: str, max_limit: int = 1000) -> QueryResult:
        """
        Execute SQL query against database (PostgreSQL or MySQL).

        Args:
            url: Database connection URL
            sql: SQL query to execute
            max_limit: Maximum number of rows to return

        Returns:
            QueryResult with columns, rows, and metadata

        Raises:
            ValueError: If SQL validation fails
            Exception: If query execution fails
        """
        # Validate SQL (SELECT only)
        is_valid, error = sql_validator.validate_select_only(sql)
        if not is_valid:
            raise ValueError(error)

        # Add LIMIT if missing
        sql_with_limit = sql_validator.add_limit_if_missing(sql, max_limit)
        
        # Detect database type
        db_type = db_connection_service.detect_database_type(url)

        # Execute query
        start_time = time.time()

        with db_connection_service.get_connection(url) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_with_limit)

            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # Fetch all rows
            rows_data = cursor.fetchall()

            # Convert to list of dicts with proper type conversion
            if db_type == "mysql":
                rows = [self._convert_mysql_row_to_dict(columns, row) for row in rows_data]
            else:
                rows = [dict(zip(columns, row)) for row in rows_data]

            cursor.close()

        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            execution_time=round(execution_time, 2),
        )

    def _convert_mysql_row_to_dict(self, columns: list[str], row: tuple) -> dict[str, Any]:
        """Convert MySQL row tuple to dictionary with proper type handling.
        
        Args:
            columns: Column names
            row: Row data tuple
            
        Returns:
            Dictionary with JSON-serializable values
        """
        result = {}
        for col, value in zip(columns, row):
            # Convert MySQL-specific types to JSON-compatible types
            if value is None:
                result[col] = None
            elif isinstance(value, (datetime, date)):
                result[col] = value.isoformat()
            elif isinstance(value, Decimal):
                result[col] = float(value)
            elif isinstance(value, bytes):
                # Convert BLOB/BINARY to base64 or string if UTF-8
                try:
                    result[col] = value.decode('utf-8')
                except UnicodeDecodeError:
                    result[col] = value.hex()
            elif isinstance(value, int) and value in (0, 1):
                # MySQL TINYINT(1) as boolean - keep as int for compatibility
                result[col] = value
            else:
                result[col] = value
        return result


# Global instance
query_executor = QueryExecutorService()
