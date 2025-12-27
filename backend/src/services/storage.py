"""SQLite database initialization and helper functions for metadata storage."""

import sqlite3
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager
import os
import json
from datetime import datetime

from src.models.database import DatabaseConnection
from src.models.metadata import DatabaseMetadata, TableMetadata


# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent.parent / "db-query" / "db_query.db"


def get_db_path() -> Path:
    """Get database path from environment or default.
    
    Returns:
        Path to SQLite database file
    """
    db_path_str = os.getenv("SQLITE_DB_PATH")
    if db_path_str:
        return Path(db_path_str)
    return DEFAULT_DB_PATH


@contextmanager
def get_connection():
    """Get SQLite database connection as context manager.
    
    Yields:
        sqlite3.Connection: Database connection
        
    Example:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM database_connections")
    """
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _migrate_add_database_type() -> None:
    """Add database_type column to existing database_connections table if it doesn't exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if database_type column exists
        cursor.execute("PRAGMA table_info(database_connections)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'database_type' not in columns:
            # Add the column with default value
            cursor.execute("""
                ALTER TABLE database_connections 
                ADD COLUMN database_type TEXT DEFAULT 'postgresql'
            """)
            print("✅ Migration: Added database_type column to database_connections table")
        
        cursor.close()


def init_database() -> None:
    """Initialize SQLite database with schema.
    
    Creates tables if they don't exist:
    - database_connections: Stores database connection URLs (PostgreSQL and MySQL)
    - database_metadata: Stores cached schema metadata as JSON
    """
    schema = """
    -- Database connections table
    CREATE TABLE IF NOT EXISTS database_connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        url TEXT NOT NULL,
        database_type TEXT DEFAULT 'postgresql',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_connected_at TIMESTAMP
    );

    -- Database metadata table (cached schema information)
    CREATE TABLE IF NOT EXISTS database_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        database_id INTEGER NOT NULL REFERENCES database_connections(id) ON DELETE CASCADE,
        tables_json TEXT NOT NULL,
        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(database_id)
    );

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_metadata_database_id ON database_metadata(database_id);
    CREATE INDEX IF NOT EXISTS idx_connections_name ON database_connections(name);
    """
    
    with get_connection() as conn:
        conn.executescript(schema)
    
    # Run migrations
    _migrate_add_database_type()


# Connection helper functions

def insert_connection(name: str, url: str, database_type: str = "postgresql") -> int:
    """Insert new database connection.
    
    Args:
        name: Unique database name
        url: Database connection URL
        database_type: Type of database (postgresql or mysql)
        
    Returns:
        ID of inserted connection
        
    Raises:
        sqlite3.IntegrityError: If name already exists
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO database_connections (name, url, database_type) VALUES (?, ?, ?)",
            (name, url, database_type),
        )
        return cursor.lastrowid


def get_all_connections() -> list[DatabaseConnection]:
    """Get all database connections.
    
    Returns:
        List of DatabaseConnection models
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM database_connections ORDER BY created_at DESC")
        return [DatabaseConnection(**dict(row)) for row in cursor.fetchall()]


def get_connection_by_name(name: str) -> DatabaseConnection | None:
    """Get database connection by name.
    
    Args:
        name: Database name
        
    Returns:
        DatabaseConnection model or None if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM database_connections WHERE name = ?", (name,))
        row = cursor.fetchone()
        return DatabaseConnection(**dict(row)) if row else None


def update_connection_url(connection_id: int, url: str) -> bool:
    """Update database connection URL by ID.
    
    Args:
        connection_id: Database connection ID
        url: New PostgreSQL connection URL
        
    Returns:
        True if updated, False if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE database_connections SET url = ? WHERE id = ?",
            (url, connection_id),
        )
        return cursor.rowcount > 0


def update_last_connected(connection_id: int) -> bool:
    """Update last_connected_at timestamp for a database connection.
    
    Args:
        connection_id: Database connection ID
        
    Returns:
        True if updated, False if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE database_connections SET last_connected_at = ? WHERE id = ?",
            (datetime.now().isoformat(), connection_id),
        )
        return cursor.rowcount > 0


def delete_connection(connection_id: int) -> bool:
    """Delete database connection and its metadata by ID.
    
    Args:
        connection_id: Database connection ID
        
    Returns:
        True if deleted, False if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM database_connections WHERE id = ?", (connection_id,))
        return cursor.rowcount > 0





# Metadata helper functions

def insert_metadata(database_id: int, tables_json: str) -> int:
    """Insert or replace database metadata.
    
    Args:
        database_id: Foreign key to database_connections
        tables_json: JSON string of table metadata
        
    Returns:
        ID of inserted metadata
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # Delete existing metadata for this database
        cursor.execute("DELETE FROM database_metadata WHERE database_id = ?", (database_id,))
        # Insert new metadata
        cursor.execute(
            "INSERT INTO database_metadata (database_id, tables_json) VALUES (?, ?)",
            (database_id, tables_json),
        )
        return cursor.lastrowid


def get_metadata_by_database_id(database_id: int) -> DatabaseMetadata | None:
    """Get metadata for a database.
    
    Args:
        database_id: Database connection ID
        
    Returns:
        DatabaseMetadata model or None if not found
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM database_metadata WHERE database_id = ?",
            (database_id,),
        )
        row = cursor.fetchone()
        if row:
            metadata_dict = dict(row)
            # Parse JSON string to TableMetadata objects
            tables_data = json.loads(metadata_dict["tables_json"])
            tables = [TableMetadata(**t) for t in tables_data]
            
            return DatabaseMetadata(
                id=metadata_dict["id"],
                database_id=metadata_dict["database_id"],
                tables=tables,
                extracted_at=datetime.fromisoformat(metadata_dict["extracted_at"]),
            )
        return None


# Initialize database on module import
init_database()
