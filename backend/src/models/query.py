"""Query execution Pydantic models."""

from typing import Any

from pydantic import Field

from src.utils.camel_case import CamelCaseModel


class QueryRequest(CamelCaseModel):
    """Request model for SQL query execution."""

    sql: str = Field(..., description="SQL query to execute")


class QueryResult(CamelCaseModel):
    """Response model for SQL query execution."""

    columns: list[str] = Field(..., description="Column names")
    rows: list[dict[str, Any]] = Field(..., description="Result rows")
    row_count: int = Field(..., description="Number of rows returned")
    execution_time: float = Field(..., description="Execution time in milliseconds")


class NaturalLanguageQueryRequest(CamelCaseModel):
    """Request model for natural language query."""

    prompt: str = Field(..., description="Natural language query prompt")


class NaturalLanguageQueryResponse(CamelCaseModel):
    """Response model for natural language query."""

    sql: str = Field(..., description="Generated SQL query")
    explanation: str = Field(..., description="Explanation of the generated SQL")
