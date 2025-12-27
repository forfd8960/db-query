"""Database connection service for PostgreSQL and MySQL."""

import re
from contextlib import contextmanager
from typing import Any, Generator, Literal, Union
from urllib.parse import urlparse

import psycopg2
from psycopg2 import OperationalError, pool
from psycopg2.extensions import connection as PgConnection
import mysql.connector
from mysql.connector import Error as MySQLError
from mysql.connector.connection import MySQLConnection


class DatabaseConnectionService:
    """Service for managing PostgreSQL and MySQL database connections."""

    def _parse_mysql_url(self, url: str) -> dict[str, Any]:
        """
        Parse MySQL connection URL into connection parameters.
        
        Args:
            url: MySQL connection URL
            
        Returns:
            Dictionary with connection parameters
        """
        parsed = urlparse(url)
        return {
            'host': parsed.hostname or 'localhost',
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password or '',
            'database': parsed.path.lstrip('/') if parsed.path else None
        }
    
    def _create_mysql_connection(self, url: str) -> MySQLConnection:
        """
        Create MySQL connection from URL.
        
        Args:
            url: MySQL connection URL
            
        Returns:
            MySQL connection object
        """
        params = self._parse_mysql_url(url)
        return mysql.connector.connect(**params)

    def detect_database_type(self, url: str) -> Literal["postgresql", "mysql"]:
        """Detect database type from connection URL.
        
        Args:
            url: Database connection URL
            
        Returns:
            Database type ("postgresql" or "mysql")
            
        Raises:
            ValueError: If URL format is unsupported
        """
        if url.startswith(("postgresql://", "postgres://")):
            return "postgresql"
        elif url.startswith("mysql://"):
            return "mysql"
        else:
            raise ValueError(f"Unsupported database URL format: {url}")

    def extract_db_name_from_url(self, url: str) -> str:
        """
        Extract database name from database URL.

        Args:
            url: Database connection URL (PostgreSQL or MySQL)

        Returns:
            Database name extracted from URL

        Raises:
            ValueError: If URL format is invalid
        """
        try:
            parsed = urlparse(url)
            db_name = parsed.path.lstrip("/")
            if not db_name:
                raise ValueError("Database name not found in URL")
            return db_name
        except Exception as e:
            raise ValueError(f"Invalid database URL: {e}") from e

    def test_connection(self, url: str) -> tuple[bool, str | None]:
        """
        Test database connection.

        Args:
            url: Database connection URL (PostgreSQL or MySQL)

        Returns:
            Tuple of (success, error_message)
        """
        db_type = self.detect_database_type(url)
        
        if db_type == "postgresql":
            return self._test_postgres_connection(url)
        else:  # mysql
            return self._test_mysql_connection(url)
    
    def _test_postgres_connection(self, url: str) -> tuple[bool, str | None]:
        """Test PostgreSQL connection."""
        try:
            conn = psycopg2.connect(url)
            conn.close()
            return (True, None)
        except OperationalError as e:
            return (False, str(e))
        except Exception as e:
            return (False, f"Unexpected error: {e}")
    
    def _test_mysql_connection(self, url: str) -> tuple[bool, str | None]:
        """Test MySQL connection."""
        try:
            conn = self._create_mysql_connection(url)
            conn.close()
            return (True, None)
        except MySQLError as e:
            return (False, str(e))
        except Exception as e:
            return (False, f"Unexpected error: {e}")

    @contextmanager
    def get_connection(self, url: str) -> Generator[Union[PgConnection, MySQLConnection], None, None]:
        """
        Get a connection to the database.

        Args:
            url: Database connection URL (PostgreSQL or MySQL)

        Yields:
            Database connection object (PostgreSQL or MySQL)

        Raises:
            OperationalError or MySQLError: If connection fails
        """
        conn = None
        db_type = self.detect_database_type(url)
        
        try:
            if db_type == "postgresql":
                conn = psycopg2.connect(url)
            else:  # mysql
                conn = self._create_mysql_connection(url)
            yield conn
        finally:
            if conn:
                conn.close()

# Global instance
db_connection_service = DatabaseConnectionService()
