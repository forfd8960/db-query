"""JSON export implementation for query results.

This module provides JSON export functionality with proper type preservation,
datetime handling, and pretty-printed formatting.
"""

import json
from datetime import date, datetime
from typing import Any

from src.utils.filename import disambiguate_column_names

from .base import BaseExporter


class JSONExporter(BaseExporter):
    """Export query results to JSON format with type preservation."""

    def export(self, columns: list[str], rows: list[dict[str, Any]]) -> bytes:
        """Export data to JSON format.

        Args:
            columns: List of column names (used for validation)
            rows: List of row dictionaries with column names as keys

        Returns:
            JSON data as UTF-8 encoded bytes

        Notes:
            - Uses ensure_ascii=False for proper Unicode support
            - Pretty-printed with 2-space indentation
            - Numbers exported as JSON numbers (not strings)
            - Null values exported as JSON null
            - Dates/datetimes converted to ISO 8601 strings
            - Non-serializable objects converted to strings as fallback
            - Handles duplicate column names with _1, _2 suffixes
        """
        # Disambiguate duplicate column names
        unique_columns = disambiguate_column_names(columns)
        
        # Remap rows to use unique column names
        remapped_rows = []
        for row in rows:
            remapped_row = {}
            for original_col, unique_col in zip(columns, unique_columns):
                remapped_row[unique_col] = row.get(original_col)
            remapped_rows.append(remapped_row)
        
        # Custom JSON encoder for handling special types
        def json_default(obj: Any) -> str:
            """Convert non-serializable objects to strings.
            
            Args:
                obj: Object to serialize
                
            Returns:
                ISO 8601 string for dates/datetimes, str() for others
            """
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            # Fallback for any other non-serializable objects
            return str(obj)

        # Export rows as JSON array
        json_string = json.dumps(
            remapped_rows,
            ensure_ascii=False,  # Allow Unicode characters
            indent=2,            # Pretty-print with 2 spaces
            default=json_default # Handle dates and other types
        )

        return json_string.encode("utf-8")
