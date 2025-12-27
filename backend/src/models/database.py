"""Database connection Pydantic models."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field, field_validator

from src.utils.camel_case import CamelCaseModel


class DatabaseConnectionCreate(CamelCaseModel):
    """Request model for creating a database connection."""

    url: str = Field(..., description="Database connection URL (PostgreSQL or MySQL)")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database connection URL format."""
        valid_prefixes = ("postgresql://", "postgres://", "mysql://")
        if not v.startswith(valid_prefixes):
            raise ValueError("URL must start with postgresql://, postgres://, or mysql://")
        return v


class DatabaseConnectionUpdate(CamelCaseModel):
    """Request model for updating a database connection."""

    url: str = Field(..., description="Database connection URL (PostgreSQL or MySQL)")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate database connection URL format."""
        valid_prefixes = ("postgresql://", "postgres://", "mysql://")
        if not v.startswith(valid_prefixes):
            raise ValueError("URL must start with postgresql://, postgres://, or mysql://")
        return v


class DatabaseConnection(CamelCaseModel):
    """Database connection model."""

    id: int
    name: str
    url: str
    database_type: Literal["postgresql", "mysql"] = Field(
        default="postgresql",
        description="Database type (postgresql or mysql)"
    )
    created_at: datetime = Field(default_factory=datetime.now)
    last_connected_at: Optional[datetime] = None

    @field_validator("created_at", "last_connected_at", mode="before")
    @classmethod
    def parse_datetime(cls, v) -> datetime | None:
        """Parse datetime from string if needed."""
        if v is None:
            return v
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        return v

    class Config:
        """Pydantic configuration."""

        from_attributes = True
