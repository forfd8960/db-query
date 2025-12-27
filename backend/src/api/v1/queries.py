"""Query execution API endpoints."""

import logging

from fastapi import APIRouter, HTTPException, status

from src.models.errors import ErrorCode, ErrorResponse
from src.models.query import NaturalLanguageQueryRequest, NaturalLanguageQueryResponse, QueryRequest, QueryResult
from src.services.db_connection import db_connection_service
from src.services.query_executor import query_executor
from src.services.storage import get_connection_by_name, update_last_connected
from src.utils.exceptions import raise_internal_error, raise_not_found, raise_validation_error

logger = logging.getLogger(__name__)
router = APIRouter(tags=["queries"])


@router.post("/databases/{db_name}/query/", response_model=QueryResult)
async def execute_query(db_name: str, data: QueryRequest) -> QueryResult:
    """
    Execute SQL query against a database.

    Args:
        db_name: Database name
        data: Query request with SQL

    Returns:
        Query results with columns and rows

    Raises:
        HTTPException: If database not found or query execution fails
    """
    # Check if database exists
    connection = get_connection_by_name(db_name)
    if not connection:
        raise_not_found("Database connection", db_name)

    # Execute query
    try:
        logger.info(f"Executing query on '{db_name}': {data.sql[:100]}...")
        result = query_executor.execute_query(connection.url, data.sql)

        # Update last_connected_at
        update_last_connected(connection.id)

        logger.info(f"Query returned {result.row_count} rows in {result.execution_time}ms")
        return result
    except ValueError as e:
        # Validation error (e.g., non-SELECT query)
        raise_validation_error(str(e))
    except Exception as e:
        # Query execution error
        raise_internal_error(f"Query execution failed: {str(e)}", e)


@router.post("/databases/{db_name}/nl-query/", response_model=NaturalLanguageQueryResponse)
async def generate_sql_from_natural_language(
    db_name: str, data: NaturalLanguageQueryRequest
) -> NaturalLanguageQueryResponse:
    """
    Generate SQL from natural language query.

    Args:
        db_name: Database name
        data: Natural language query request

    Returns:
        Generated SQL and explanation

    Raises:
        HTTPException: If database not found or generation fails
    """
    # Check if database exists
    connection = get_connection_by_name(db_name)
    if not connection:
        raise_not_found("Database connection", db_name)

    # Import here to avoid loading OpenAI if not needed
    try:
        from src.services.nl_converter import get_nl_converter

        logger.info(f"Generating SQL for '{db_name}': {data.prompt}")
        nl_converter = get_nl_converter()
        result = await nl_converter.convert_to_sql(
            connection.url, connection.id, data.prompt, connection.database_type
        )
        logger.info(f"Generated SQL: {result.sql[:100]}...")
        return result
    except ImportError:
        logger.error("Natural language query feature not available (OpenAI not configured)")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=ErrorResponse(
                message="Natural language query feature not available",
                code=ErrorCode.INTERNAL_ERROR,
            ).model_dump(by_alias=True),
        )
    except Exception as e:
        raise_internal_error(f"Failed to generate SQL: {str(e)}", e)
