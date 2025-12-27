"""Error response models for API error handling."""

from typing import Optional, Any
from enum import Enum
from src.utils.camel_case import CamelCaseModel


class ErrorCode(str, Enum):
    """Standard error codes for API responses."""
    
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SQL_VALIDATION_ERROR = "SQL_VALIDATION_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorResponse(CamelCaseModel):
    """Standard error response model.
    
    Attributes:
        message: Human-readable error message
        code: Error code from ErrorCode enum
        details: Optional additional error context (dict with any structure)
        
    Example:
        ErrorResponse(
            message="Only SELECT statements are allowed",
            code=ErrorCode.SQL_VALIDATION_ERROR,
            details={"statementType": "UPDATE", "line": 1, "column": 1}
        )
        
    JSON Output:
        {
            "message": "Only SELECT statements are allowed",
            "code": "SQL_VALIDATION_ERROR",
            "details": {
                "statementType": "UPDATE",
                "line": 1,
                "column": 1
            }
        }
    """
    
    message: str
    code: ErrorCode
    details: Optional[dict[str, Any]] = None
