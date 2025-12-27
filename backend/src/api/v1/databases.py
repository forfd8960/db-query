"""Database connection API endpoints."""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from src.models.database import DatabaseConnection, DatabaseConnectionCreate, DatabaseConnectionUpdate
from src.models.errors import ErrorCode, ErrorResponse
from src.models.metadata import DatabaseMetadataResponse
from src.services.db_connection import db_connection_service
from src.services.metadata_extractor import metadata_extractor
from src.services.storage import (
    delete_connection,
    get_all_connections,
    get_connection_by_name,
    get_metadata_by_database_id,
    insert_connection,
    insert_metadata,
    update_connection_url,
)
from src.utils.exceptions import (
    raise_connection_failed,
    raise_internal_error,
    raise_not_found,
    raise_validation_error,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/databases", tags=["databases"])


@router.post("/", response_model=DatabaseConnection, status_code=status.HTTP_201_CREATED)
async def create_database(data: DatabaseConnectionCreate) -> DatabaseConnection:
    """
    Create a new database connection.

    Args:
        data: Database connection creation data

    Returns:
        Created database connection

    Raises:
        HTTPException: If connection test fails or database name already exists
    """
    logger.info(f"Creating database connection: {data.url}")

    # Test connection
    success, error = db_connection_service.test_connection(data.url)
    if not success:
        raise_connection_failed(error or "Unknown error")

    # Extract database name from URL
    try:
        db_name = db_connection_service.extract_db_name_from_url(data.url)
        db_type = db_connection_service.detect_database_type(data.url)
    except ValueError as e:
        raise_validation_error(str(e))

    # Check if database name already exists
    existing = get_connection_by_name(db_name)
    if existing:
        raise_validation_error(f"Database connection with name '{db_name}' already exists")

    # Insert connection
    connection_id = insert_connection(db_name, data.url, db_type)
    logger.info(f"Created database connection '{db_name}' with ID {connection_id}")

    # Return created connection
    conn = get_connection_by_name(db_name)
    if not conn:
        raise_internal_error("Failed to retrieve created connection")

    return conn


@router.get("/", response_model=list[DatabaseConnection])
async def list_databases() -> list[DatabaseConnection]:
    """
    List all database connections.

    Returns:
        List of all database connections
    """
    return get_all_connections()


@router.put("/{db_name}/", response_model=DatabaseConnection)
async def update_database(db_name: str, data: DatabaseConnectionUpdate) -> DatabaseConnection:
    """
    Update a database connection.

    Args:
        db_name: Database name
        data: Updated connection data

    Returns:
        Updated database connection

    Raises:
        HTTPException: If database not found or connection test fails
    """
    # Check if database exists
    existing = get_connection_by_name(db_name)
    if not existing:
        raise_not_found("Database connection", db_name)

    # Test new connection
    success, error = db_connection_service.test_connection(data.url)
    if not success:
        raise_connection_failed(error or "Unknown error")

    # Update connection
    update_connection_url(existing.id, data.url)
    logger.info(f"Updated database connection '{db_name}'")

    # Return updated connection
    conn = get_connection_by_name(db_name)
    if not conn:
        raise_internal_error("Failed to retrieve updated connection")

    return conn


@router.delete("/{db_name}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(db_name: str) -> None:
    """
    Delete a database connection and its metadata.

    Args:
        db_name: Database name

    Raises:
        HTTPException: If database not found
    """
    # Check if database exists
    existing = get_connection_by_name(db_name)
    if not existing:
        raise_not_found("Database connection", db_name)

    # Delete connection (CASCADE will delete metadata)
    delete_connection(existing.id)
    logger.info(f"Deleted database connection '{db_name}'")


@router.get("/{db_name}/metadata/", response_model=DatabaseMetadataResponse)
async def get_database_metadata(db_name: str, refresh: bool = False) -> DatabaseMetadataResponse:
    """
    Get database metadata (tables, columns, etc.).

    Args:
        db_name: Database name
        refresh: If True, extract fresh metadata; if False, use cached if available

    Returns:
        Database metadata

    Raises:
        HTTPException: If database not found or metadata extraction fails
    """
    # Check if database exists
    connection = get_connection_by_name(db_name)
    if not connection:
        raise_not_found("Database connection", db_name)

    # Check for cached metadata
    if not refresh:
        cached = get_metadata_by_database_id(connection.id)
        if cached:
            logger.debug(f"Returning cached metadata for '{db_name}'")
            return DatabaseMetadataResponse.from_metadata(db_name, cached)

    # Extract fresh metadata
    try:
        logger.info(f"Extracting fresh metadata for '{db_name}'")
        metadata = metadata_extractor.extract_metadata(connection.url, connection.id)

        # Cache metadata
        tables_json = json.dumps([t.model_dump(by_alias=True) for t in metadata.tables])
        insert_metadata(connection.id, tables_json)

        # Update last_connected_at
        from src.services.storage import update_last_connected

        update_last_connected(connection.id)

        logger.info(f"Extracted {len(metadata.tables)} tables for '{db_name}'")
        return DatabaseMetadataResponse.from_metadata(db_name, metadata)
    except Exception as e:
        raise_internal_error(f"Failed to extract metadata: {str(e)}", e)
