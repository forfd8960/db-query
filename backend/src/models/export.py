"""Export-related Pydantic models."""

from enum import Enum
from typing import Any

from pydantic import ConfigDict, Field

from src.utils.camel_case import CamelCaseModel


class ExportFormat(str, Enum):
    """Supported export file formats."""

    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"


class ExportRequest(CamelCaseModel):
    """Request model for exporting query results."""
    
    # Override strict mode for this model to allow string -> enum conversion
    model_config = ConfigDict(
        alias_generator=CamelCaseModel.model_config["alias_generator"],
        populate_by_name=True,
        from_attributes=True,
        strict=False,  # Allow string to enum conversion
    )

    format: ExportFormat = Field(..., description="Export file format")
    query_results: dict[str, Any] = Field(
        ...,
        description="Query results to export (columns, rows, rowCount, executionTime)",
    )
