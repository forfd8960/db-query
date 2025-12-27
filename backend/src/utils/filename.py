"""Filename sanitization and generation utilities."""

import re
from datetime import datetime


def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename by removing unsafe characters.

    Args:
        name: Original filename

    Returns:
        Sanitized filename safe for filesystems

    Examples:
        >>> sanitize_filename("my/database:name")
        'my_database_name'
        >>> sanitize_filename("test<file>")
        'test_file_'
    """
    # Remove unsafe characters: / \ : * ? " < > |
    name = re.sub(r'[/<>:"|?*\\]', '_', name)
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    # Limit length to 200 characters
    return name[:200]


def generate_filename(db_name: str, file_format: str) -> str:
    """
    Generate a filename for export files.

    Format: {sanitized_db_name}_{timestamp}.{extension}

    Args:
        db_name: Database name
        file_format: File format (csv, json, excel)

    Returns:
        Generated filename with timestamp

    Examples:
        >>> generate_filename("mydb", "csv")  # doctest: +SKIP
        'mydb_2025-12-27_143022.csv'
    """
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    safe_db_name = sanitize_filename(db_name)
    extension = "xlsx" if file_format == "excel" else file_format
    return f"{safe_db_name}_{timestamp}.{extension}"


def disambiguate_column_names(columns: list[str]) -> list[str]:
    """
    Handle duplicate column names by appending numeric suffixes.

    Args:
        columns: List of column names (may contain duplicates)

    Returns:
        List of unique column names with suffixes for duplicates

    Examples:
        >>> disambiguate_column_names(["id", "name", "id"])
        ['id', 'name', 'id_1']
        >>> disambiguate_column_names(["value", "value", "value"])
        ['value', 'value_1', 'value_2']
    """
    seen: dict[str, int] = {}
    result: list[str] = []

    for col in columns:
        if col in seen:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            result.append(col)

    return result
