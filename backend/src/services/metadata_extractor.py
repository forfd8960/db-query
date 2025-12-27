"""Database metadata extraction service for PostgreSQL and MySQL."""

from datetime import datetime
from typing import Union

from psycopg2.extensions import connection as PgConnection
from mysql.connector.connection import MySQLConnection

from src.models.metadata import ColumnMetadata, DatabaseMetadata, TableMetadata
from src.services.db_connection import db_connection_service


class MetadataExtractorService:
    """Service for extracting database metadata from PostgreSQL and MySQL."""

    def extract_metadata(self, url: str, database_id: int) -> DatabaseMetadata:
        """
        Extract metadata from database (PostgreSQL or MySQL).

        Args:
            url: Database connection URL
            database_id: ID of the database connection record

        Returns:
            DatabaseMetadata object with extracted schema information

        Raises:
            Exception: If metadata extraction fails
        """
        db_type = db_connection_service.detect_database_type(url)
        
        with db_connection_service.get_connection(url) as conn:
            if db_type == "postgresql":
                tables = self._extract_postgres_tables_and_views(conn)
            else:  # mysql
                tables = self._extract_mysql_tables_and_views(conn)

            return DatabaseMetadata(
                id=0,  # Will be set by storage layer
                database_id=database_id,
                tables=tables,
                extracted_at=datetime.now(),
            )

    def _extract_postgres_tables_and_views(self, conn: PgConnection) -> list[TableMetadata]:
        """Extract all tables and views from PostgreSQL database."""
        query = """
            SELECT 
                t.table_schema,
                t.table_name,
                t.table_type
            FROM information_schema.tables t
            WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY t.table_schema, t.table_name
        """

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        tables = []
        for schema, table_name, table_type in rows:
            # Get columns for this table
            columns = self._extract_columns(conn, schema, table_name)

            # Get approximate row count for tables (not views)
            row_count = None
            if table_type == "BASE TABLE":
                row_count = self._get_row_count(conn, schema, table_name)

            tables.append(
                TableMetadata(
                    name=table_name,
                    schema_name=schema,
                    table_type="table" if table_type == "BASE TABLE" else "view",
                    columns=columns,
                    row_count=row_count,
                )
            )

        cursor.close()
        return tables

    def _extract_columns(self, conn: PgConnection, schema: str, table_name: str) -> list[ColumnMetadata]:
        """Extract columns for a specific table."""
        query = """
            SELECT 
                c.column_name,
                c.data_type,
                c.is_nullable,
                c.column_default,
                CASE 
                    WHEN pk.column_name IS NOT NULL THEN true 
                    ELSE false 
                END as is_primary_key
            FROM information_schema.columns c
            LEFT JOIN (
                SELECT ku.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage ku
                    ON tc.constraint_name = ku.constraint_name
                    AND tc.table_schema = ku.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY'
                    AND tc.table_schema = %s
                    AND tc.table_name = %s
            ) pk ON c.column_name = pk.column_name
            WHERE c.table_schema = %s
                AND c.table_name = %s
            ORDER BY c.ordinal_position
        """

        cursor = conn.cursor()
        cursor.execute(query, (schema, table_name, schema, table_name))
        rows = cursor.fetchall()

        columns = []
        for col_name, data_type, is_nullable, col_default, is_pk in rows:
            columns.append(
                ColumnMetadata(
                    name=col_name,
                    data_type=data_type,
                    is_nullable=is_nullable == "YES",
                    column_default=col_default,
                    is_primary_key=is_pk,
                )
            )

        cursor.close()
        return columns

    def _get_row_count(self, conn: PgConnection, schema: str, table_name: str) -> int | None:
        """Get approximate row count for a table."""
        try:
            cursor = conn.cursor()
            # Use pg_class for fast approximate count
            query = """
                SELECT reltuples::bigint AS row_count
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = %s
                    AND c.relname = %s
            """
            cursor.execute(query, (schema, table_name))
            result = cursor.fetchone()
            cursor.close()

            return int(result[0]) if result and result[0] else None
        except Exception:
            return None

    # MySQL metadata extraction methods
    
    def _extract_mysql_tables_and_views(self, conn: MySQLConnection) -> list[TableMetadata]:
        """Extract all tables and views from MySQL database."""
        query = """
            SELECT 
                TABLE_SCHEMA,
                TABLE_NAME,
                TABLE_TYPE
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY TABLE_SCHEMA, TABLE_NAME
        """

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        tables = []
        for schema, table_name, table_type in rows:
            # Get columns for this table
            columns = self._extract_mysql_columns(conn, schema, table_name)

            # Get approximate row count for tables (not views)
            row_count = None
            if table_type == "BASE TABLE":
                row_count = self._get_mysql_row_count(conn, schema, table_name)

            tables.append(
                TableMetadata(
                    name=table_name,
                    schema_name=schema,
                    table_type="table" if table_type == "BASE TABLE" else "view",
                    columns=columns,
                    row_count=row_count,
                )
            )

        cursor.close()
        return tables

    def _extract_mysql_columns(self, conn: MySQLConnection, schema: str, table_name: str) -> list[ColumnMetadata]:
        """Extract columns for a specific MySQL table."""
        query = """
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """

        cursor = conn.cursor()
        cursor.execute(query, (schema, table_name))
        rows = cursor.fetchall()

        columns = []
        for col_name, data_type, is_nullable, col_default, column_key in rows:
            columns.append(
                ColumnMetadata(
                    name=col_name,
                    data_type=data_type,
                    is_nullable=is_nullable == "YES",
                    column_default=col_default,
                    is_primary_key=(column_key == "PRI"),
                )
            )

        cursor.close()
        return columns

    def _get_mysql_row_count(self, conn: MySQLConnection, schema: str, table_name: str) -> int | None:
        """Get approximate row count for a MySQL table."""
        try:
            cursor = conn.cursor()
            query = """
                SELECT TABLE_ROWS 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            """
            cursor.execute(query, (schema, table_name))
            result = cursor.fetchone()
            cursor.close()

            return int(result[0]) if result and result[0] else None
        except Exception:
            return None


# Global instance
metadata_extractor = MetadataExtractorService()
