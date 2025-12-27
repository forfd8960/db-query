"""Database metadata Pydantic models."""

from datetime import datetime
from typing import Any

from pydantic import Field

from src.utils.camel_case import CamelCaseModel


class ColumnMetadata(CamelCaseModel):
    """Column metadata model."""

    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="PostgreSQL data type")
    is_nullable: bool = Field(..., description="Whether column allows NULL values")
    column_default: str | None = Field(None, description="Default value expression")
    is_primary_key: bool = Field(False, description="Whether column is part of primary key")


class TableMetadata(CamelCaseModel):
    """Table metadata model."""

    name: str = Field(..., description="Table name")
    schema_name: str = Field(..., description="Schema name (e.g., 'public')", alias="schema")
    table_type: str = Field(..., description="Table type: 'table' or 'view'")
    columns: list[ColumnMetadata] = Field(default_factory=list, description="Table columns")
    row_count: int | None = Field(None, description="Approximate row count")


class DatabaseMetadata(CamelCaseModel):
    """Database metadata model."""

    id: int
    database_id: int
    tables: list[TableMetadata] = Field(default_factory=list, description="Database tables and views")
    extracted_at: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class DatabaseMetadataResponse(CamelCaseModel):
    """Response model for database metadata."""

    database_name: str
    tables: list[TableMetadata]
    extracted_at: datetime
    table_count: int
    view_count: int

    @staticmethod
    def from_metadata(db_name: str, metadata: DatabaseMetadata) -> "DatabaseMetadataResponse":
        """Create response from DatabaseMetadata model."""
        table_count = sum(1 for t in metadata.tables if t.table_type == "table")
        view_count = sum(1 for t in metadata.tables if t.table_type == "view")

        return DatabaseMetadataResponse(
            database_name=db_name,
            tables=metadata.tables,
            extracted_at=metadata.extracted_at,
            table_count=table_count,
            view_count=view_count,
        )
