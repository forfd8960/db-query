"""API exception utilities for consistent error handling."""

import logging
from typing import Any

from fastapi import HTTPException, status

from src.models.errors import ErrorCode, ErrorResponse

logger = logging.getLogger(__name__)


def raise_api_error(
    status_code: int,
    message: str,
    code: ErrorCode,
    details: dict[str, Any] | None = None,
    log_error: bool = True,
) -> None:
    """
    Raise HTTPException with standardized ErrorResponse format.
    
    Args:
        status_code: HTTP status code
        message: Human-readable error message
        code: ErrorCode enum value
        details: Optional additional error context
        log_error: Whether to log the error (default True)
        
    Raises:
        HTTPException: Always raises with formatted error response
        
    Example:
        raise_api_error(
            status.HTTP_404_NOT_FOUND,
            "Database connection 'mydb' not found",
            ErrorCode.NOT_FOUND
        )
    """
    if log_error:
        logger.error(f"{code}: {message}", extra={"details": details})
    
    raise HTTPException(
        status_code=status_code,
        detail=ErrorResponse(
            message=message,
            code=code,
            details=details,
        ).model_dump(by_alias=True),
    )


def raise_not_found(resource: str, identifier: str) -> None:
    """Raise 404 Not Found error."""
    raise_api_error(
        status.HTTP_404_NOT_FOUND,
        f"{resource} '{identifier}' not found",
        ErrorCode.NOT_FOUND,
    )


def raise_connection_failed(error_msg: str) -> None:
    """Raise 400 Bad Request for connection failures."""
    raise_api_error(
        status.HTTP_400_BAD_REQUEST,
        f"Failed to connect to database: {error_msg}",
        ErrorCode.CONNECTION_FAILED,
    )


def raise_validation_error(message: str, details: dict[str, Any] | None = None) -> None:
    """Raise 400 Bad Request for validation errors."""
    raise_api_error(
        status.HTTP_400_BAD_REQUEST,
        message,
        ErrorCode.VALIDATION_ERROR,
        details=details,
    )


def raise_internal_error(message: str, original_error: Exception | None = None) -> None:
    """Raise 500 Internal Server Error."""
    details = {"error": str(original_error)} if original_error else None
    raise_api_error(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        message,
        ErrorCode.INTERNAL_ERROR,
        details=details,
    )
