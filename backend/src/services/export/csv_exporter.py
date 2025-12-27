"""CSV export implementation for query results.

This module provides CSV export functionality with UTF-8 encoding,
proper special character escaping, and null value handling.
"""

import csv
import io
from typing import Any

from src.utils.filename import disambiguate_column_names

from .base import BaseExporter


class CSVExporter(BaseExporter):
    """Export query results to CSV format with UTF-8 encoding."""

    def export(self, columns: list[str], rows: list[dict[str, Any]]) -> bytes:
        """Export data to CSV format.

        Args:
            columns: List of column names (order preserved)
            rows: List of row dictionaries with column names as keys

        Returns:
            CSV data as UTF-8 encoded bytes with BOM for Excel compatibility

        Notes:
            - Uses QUOTE_MINIMAL for efficient escaping
            - Handles special characters (commas, quotes, newlines)
            - Converts None values to empty strings
            - Empty result sets produce header row only
            - Includes UTF-8 BOM for better Excel compatibility
            - Handles duplicate column names with _1, _2 suffixes
        """
        # Disambiguate duplicate column names
        unique_columns = disambiguate_column_names(columns)
        
        # Use StringIO for in-memory CSV writing
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Write header row
        writer.writerow(unique_columns)

        # Write data rows
        for row in rows:
            # Convert row dict to ordered list matching column order
            # Handle None values by converting to empty string
            csv_row = [
                "" if row.get(col) is None else str(row.get(col, ""))
                for col in columns
            ]
            writer.writerow(csv_row)

        # Get CSV string and encode to UTF-8 with BOM
        csv_string = output.getvalue()
        # Add UTF-8 BOM for Excel compatibility
        return ("\ufeff" + csv_string).encode("utf-8")
