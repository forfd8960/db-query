"""Pydantic configuration utilities for camelCase serialization."""

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase.
    
    Args:
        string: Snake case string (e.g., "created_at")
        
    Returns:
        Camel case string (e.g., "createdAt")
        
    Examples:
        >>> to_camel("created_at")
        'createdAt'
        >>> to_camel("user_name")
        'userName'
        >>> to_camel("id")
        'id'
    """
    components = string.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


class CamelCaseModel(BaseModel):
    """Base model with camelCase serialization.
    
    All models inheriting from this will automatically:
    - Convert snake_case field names to camelCase in JSON output
    - Accept both snake_case and camelCase input
    - Use strict type validation
    
    Example:
        class User(CamelCaseModel):
            user_name: str
            created_at: datetime
            
        user = User(user_name="Alice", created_at=datetime.now())
        user.model_dump()  # {"userName": "Alice", "createdAt": "2025-12-17T..."}
    """
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Accept both snake_case and camelCase in input
        from_attributes=True,   # Support ORM models
        strict=True,            # Strict type validation
    )
