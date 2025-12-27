"""Integration tests for MySQL support."""

import pytest
from src.services.db_connection import db_connection_service
from src.services.metadata_extractor import metadata_extractor
from src.services.query_executor import query_executor


# MySQL connection URL for local testing
MYSQL_TEST_URL = "mysql://root@localhost/myapp1"


def test_mysql_database_type_detection():
    """Test database type detection for MySQL URLs."""
    assert db_connection_service.detect_database_type(MYSQL_TEST_URL) == "mysql"
    assert db_connection_service.detect_database_type("mysql://user:pass@host/db") == "mysql"
    assert db_connection_service.detect_database_type("postgresql://user@host/db") == "postgresql"


def test_mysql_connection():
    """Test MySQL connection."""
    success, error = db_connection_service.test_connection(MYSQL_TEST_URL)
    assert success is True
    assert error is None


def test_mysql_db_name_extraction():
    """Test extracting database name from MySQL URL."""
    db_name = db_connection_service.extract_db_name_from_url(MYSQL_TEST_URL)
    assert db_name == "myapp1"


def test_mysql_metadata_extraction():
    """Test MySQL metadata extraction."""
    metadata = metadata_extractor.extract_metadata(MYSQL_TEST_URL, database_id=1)
    
    # Should extract tables
    assert len(metadata.tables) > 0
    
    # Check todos table exists
    todos_table = next((t for t in metadata.tables if t.name == "todos"), None)
    assert todos_table is not None
    assert todos_table.schema_name == "myapp1"
    assert todos_table.table_type == "table"
    
    # Check columns
    assert len(todos_table.columns) > 0
    
    # Check for expected columns
    column_names = [col.name for col in todos_table.columns]
    assert "id" in column_names
    assert "title" in column_names
    
    # Check primary key detection
    id_column = next(col for col in todos_table.columns if col.name == "id")
    assert id_column.is_primary_key is True


def test_mysql_query_execution():
    """Test MySQL query execution."""
    result = query_executor.execute_query(MYSQL_TEST_URL, "SELECT * FROM todos LIMIT 5")
    
    assert result.row_count <= 5
    assert len(result.columns) > 0
    assert "id" in result.columns
    assert "title" in result.columns
    assert result.execution_time > 0


def test_mysql_query_limit_enforcement():
    """Test that LIMIT is auto-appended to MySQL queries."""
    # Query without LIMIT should auto-append LIMIT 1000
    result = query_executor.execute_query(MYSQL_TEST_URL, "SELECT * FROM todos")
    
    # Should return at most 1000 rows
    assert result.row_count <= 1000


def test_mysql_select_only_validation():
    """Test that non-SELECT queries are rejected for MySQL."""
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        query_executor.execute_query(MYSQL_TEST_URL, "DELETE FROM todos WHERE id = 1")
    
    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        query_executor.execute_query(MYSQL_TEST_URL, "UPDATE todos SET title = 'test' WHERE id = 1")


def test_mysql_data_type_conversion():
    """Test MySQL data type conversion to JSON-compatible types."""
    result = query_executor.execute_query(MYSQL_TEST_URL, "SELECT * FROM todos LIMIT 1")
    
    if result.rows:
        first_row = result.rows[0]
        
        # Check that all values are JSON-serializable
        import json
        json_str = json.dumps(first_row)
        assert json_str is not None
        
        # Verify data types
        assert isinstance(first_row.get("id"), int)
        if "title" in first_row:
            assert isinstance(first_row["title"], (str, type(None)))


def test_mysql_with_backticks():
    """Test MySQL query with backtick identifiers."""
    result = query_executor.execute_query(
        MYSQL_TEST_URL, 
        "SELECT `id`, `title` FROM `todos` LIMIT 5"
    )
    
    assert result.row_count <= 5
    assert "id" in result.columns
    assert "title" in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
