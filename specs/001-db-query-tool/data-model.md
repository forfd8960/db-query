# Data Model: Database Query Tool

**Purpose**: Define entities, relationships, and data structures for the database query tool.  
**Date**: 2025-12-16  
**Status**: Complete

## Overview

This document defines the data models used throughout the application, both for local storage (SQLite) and runtime operations (API requests/responses). All models align with Constitution Principle III (Pydantic with camelCase serialization).

## Core Entities

### Database Connection

Represents a PostgreSQL database connection.

**Attributes**:
- `id`: Integer (auto-increment, primary key)
- `name`: String (unique identifier, derived from database name in URL)
- `url`: String (PostgreSQL connection URL: `postgresql://user:pass@host:port/dbname`)
- `created_at`: Timestamp (ISO 8601 format)
- `last_connected_at`: Timestamp (nullable, ISO 8601 format)

**Validation Rules**:
- URL must match PostgreSQL connection string format
- Name extracted from URL or provided by user
- Name must be unique across all connections

**Storage**: SQLite table `database_connections`

**Pydantic Model** (Backend):
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class DatabaseConnectionCreate(BaseModel):
    url: str = Field(..., description="PostgreSQL connection URL")
    
    @validator('url')
    def validate_postgres_url(cls, v):
        if not v.startswith('postgresql://'):
            raise ValueError('URL must start with postgresql://')
        return v
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )  # snake_case → camelCase

class DatabaseConnection(BaseModel):
    id: int
    name: str
    url: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_connected_at: Optional[datetime] = None
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
        populate_by_name = True
```

**TypeScript Interface** (Frontend):
```typescript
export interface DatabaseConnection {
  id: number;
  name: string;
  url: string;
  createdAt: string;  // ISO 8601
  lastConnectedAt?: string;  // ISO 8601, optional
}

export interface DatabaseConnectionCreate {
  url: string;
}
```

**Relationships**:
- One-to-One with `DatabaseMetadata` (each connection has one metadata snapshot)
- One-to-Many with `QueryExecution` (each connection can have multiple queries)

---

### Database Metadata

Represents cached schema information for a PostgreSQL database.

**Attributes**:
- `id`: Integer (auto-increment, primary key)
- `database_id`: Integer (foreign key to `database_connections.id`)
- `tables`: Array of `TableMetadata` objects (stored as JSON)
- `extracted_at`: Timestamp (ISO 8601 format)

**Storage**: SQLite table `database_metadata`, with `tables` column as JSON TEXT

**Pydantic Model** (Backend):
```python
class DatabaseMetadata(BaseModel):
    id: int
    database_id: int
    tables: list['TableMetadata']
    extracted_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export interface DatabaseMetadata {
  id: number;
  databaseId: number;
  tables: TableMetadata[];
  extractedAt: string;  // ISO 8601
}
```

---

### Table Metadata

Represents schema information for a single table or view.

**Attributes**:
- `schema_name`: String (PostgreSQL schema, typically "public")
- `table_name`: String (table or view name)
- `table_type`: Enum ("TABLE" | "VIEW")
- `columns`: Array of `ColumnMetadata` objects

**Storage**: Nested within `DatabaseMetadata.tables` as JSON

**Pydantic Model** (Backend):
```python
from enum import Enum

class TableType(str, Enum):
    TABLE = "TABLE"
    VIEW = "VIEW"

class TableMetadata(BaseModel):
    schema_name: str
    table_name: str
    table_type: TableType
    columns: list['ColumnMetadata']
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export type TableType = 'TABLE' | 'VIEW';

export interface TableMetadata {
  schemaName: string;
  tableName: string;
  tableType: TableType;
  columns: ColumnMetadata[];
}
```

---

### Column Metadata

Represents information about a table column.

**Attributes**:
- `column_name`: String (column name)
- `data_type`: String (PostgreSQL data type: "integer", "text", "timestamp", etc.)
- `is_nullable`: Boolean (whether column accepts NULL)
- `column_default`: String (nullable, default value expression)
- `ordinal_position`: Integer (column order in table)

**Storage**: Nested within `TableMetadata.columns` as JSON

**Pydantic Model** (Backend):
```python
class ColumnMetadata(BaseModel):
    column_name: str
    data_type: str
    is_nullable: bool
    column_default: Optional[str] = None
    ordinal_position: int
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export interface ColumnMetadata {
  columnName: string;
  dataType: string;
  isNullable: boolean;
  columnDefault?: string;
  ordinalPosition: number;
}
```

---

### Query Request

Represents a SQL query execution request.

**Attributes**:
- `sql`: String (SQL SELECT statement)

**Validation Rules**:
- SQL must parse correctly via sqlparse
- SQL must be SELECT statement only (other types rejected)
- SQL without LIMIT automatically gets "LIMIT 1000" appended

**Pydantic Model** (Backend):
```python
class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1, description="SQL SELECT statement")
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export interface QueryRequest {
  sql: string;
}
```

---

### Query Result

Represents the output of a successful query execution.

**Attributes**:
- `columns`: Array of column definition objects
  - `name`: String (column name)
  - `type`: String (data type)
- `rows`: Array of row objects (each row is key-value map with camelCase keys)
- `row_count`: Integer (number of rows returned)
- `execution_time_ms`: Integer (query execution duration in milliseconds)

**Pydantic Model** (Backend):
```python
class ColumnDefinition(BaseModel):
    name: str
    type: str
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )

class QueryResult(BaseModel):
    columns: list[ColumnDefinition]
    rows: list[dict[str, Any]]  # Each dict has camelCase keys
    row_count: int
    execution_time_ms: int
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export interface ColumnDefinition {
  name: string;
  type: string;
}

export interface QueryResult {
  columns: ColumnDefinition[];
  rows: Record<string, any>[];  // camelCase keys
  rowCount: number;
  executionTimeMs: number;
}
```

**Example Response**:
```json
{
  "columns": [
    {"name": "userId", "type": "integer"},
    {"name": "userName", "type": "text"},
    {"name": "createdAt", "type": "timestamp"}
  ],
  "rows": [
    {"userId": 1, "userName": "Alice", "createdAt": "2025-01-01T12:00:00Z"},
    {"userId": 2, "userName": "Bob", "createdAt": "2025-01-02T15:30:00Z"}
  ],
  "rowCount": 2,
  "executionTimeMs": 45
}
```

---

### Natural Language Query Request

Represents a natural language query request.

**Attributes**:
- `nl_query`: String (natural language description of desired query)

**Pydantic Model** (Backend):
```python
class NaturalLanguageQueryRequest(BaseModel):
    nl_query: str = Field(..., min_length=1, description="Natural language query description")
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export interface NaturalLanguageQueryRequest {
  nlQuery: string;
}
```

---

### Natural Language Query Response

Represents the response from natural language to SQL conversion.

**Attributes**:
- `generated_sql`: String (LLM-generated SQL query)
- `confidence`: Float (optional, LLM confidence score 0-1)

**Pydantic Model** (Backend):
```python
class NaturalLanguageQueryResponse(BaseModel):
    generated_sql: str
    confidence: Optional[float] = None
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export interface NaturalLanguageQueryResponse {
  generatedSql: string;
  confidence?: number;
}
```

---

### Error Response

Represents API error responses.

**Attributes**:
- `message`: String (human-readable error message)
- `code`: String (error code: "VALIDATION_ERROR", "CONNECTION_ERROR", "SQL_ERROR", etc.)
- `details`: Object (optional, additional error context)

**Pydantic Model** (Backend):
```python
class ErrorResponse(BaseModel):
    message: str
    code: str
    details: Optional[dict[str, Any]] = None
    
    class Config:
        alias_generator = lambda x: ''.join(
            word.capitalize() if i > 0 else word 
            for i, word in enumerate(x.split('_'))
        )
```

**TypeScript Interface** (Frontend):
```typescript
export interface ErrorResponse {
  message: string;
  code: string;
  details?: Record<string, any>;
}
```

**Example Error Response**:
```json
{
  "message": "Only SELECT statements are allowed",
  "code": "SQL_VALIDATION_ERROR",
  "details": {
    "statementType": "UPDATE",
    "line": 1,
    "column": 1
  }
}
```

---

## Entity Relationships

```
DatabaseConnection (1) ←→ (1) DatabaseMetadata
       ↓
   contains
       ↓
DatabaseMetadata (1) → (*) TableMetadata
       ↓
   contains
       ↓
TableMetadata (1) → (*) ColumnMetadata
```

**Notes**:
- `DatabaseConnection` and `DatabaseMetadata` are persisted in SQLite
- `TableMetadata` and `ColumnMetadata` are stored as JSON within `DatabaseMetadata`
- `QueryRequest`, `QueryResult`, `NaturalLanguageQueryRequest`, `NaturalLanguageQueryResponse`, and `ErrorResponse` are transient (not persisted)

## SQLite Schema

```sql
-- Database connections table
CREATE TABLE database_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_connected_at TIMESTAMP
);

-- Database metadata table (cached schema information)
CREATE TABLE database_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    database_id INTEGER NOT NULL REFERENCES database_connections(id) ON DELETE CASCADE,
    tables_json TEXT NOT NULL,  -- JSON array of TableMetadata objects
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(database_id)  -- One metadata snapshot per database
);

-- Indexes for performance
CREATE INDEX idx_metadata_database_id ON database_metadata(database_id);
CREATE INDEX idx_connections_name ON database_connections(name);
```

## Data Flow

### Database Connection Flow
1. User submits connection URL (POST /api/v1/databases/)
2. Backend validates URL format
3. Backend extracts database name from URL
4. Backend stores connection in SQLite
5. Backend returns `DatabaseConnection` object to frontend

### Metadata Extraction Flow
1. Frontend requests metadata (GET /api/v1/databases/{db_name}/metadata/)
2. Backend checks SQLite cache
3. If cache miss or stale:
   - Connect to PostgreSQL
   - Query `information_schema.tables` and `information_schema.columns`
   - Transform to `TableMetadata` array
   - Store in SQLite as JSON
4. Return `DatabaseMetadata` to frontend

### Query Execution Flow
1. Frontend submits SQL (POST /api/v1/databases/{db_name}/query/)
2. Backend validates with sqlparse
3. Backend checks statement type (must be SELECT)
4. Backend adds LIMIT if missing
5. Backend executes on PostgreSQL
6. Backend transforms result to `QueryResult` (camelCase keys)
7. Return `QueryResult` to frontend

### Natural Language Query Flow
1. Frontend submits natural language (POST /api/v1/databases/{db_name}/nl-query/)
2. Backend retrieves database metadata from cache
3. Backend constructs LLM prompt with schema context
4. Backend calls OpenAI API
5. Backend receives generated SQL
6. Backend returns `NaturalLanguageQueryResponse` to frontend
7. Frontend displays SQL in editor for user review
8. User can edit and execute via normal query flow

## Validation Rules Summary

| Entity | Field | Validation |
|--------|-------|------------|
| DatabaseConnectionCreate | url | Must start with `postgresql://` |
| QueryRequest | sql | Must parse via sqlparse, must be SELECT |
| NaturalLanguageQueryRequest | nl_query | Minimum length 1 character |
| TableMetadata | table_type | Must be "TABLE" or "VIEW" |

## CamelCase Conversion

All Pydantic models use `alias_generator` to convert snake_case field names to camelCase in JSON responses. This ensures frontend consistency without manual mapping.

**Example**:
```python
# Backend model
class Example(BaseModel):
    created_at: datetime
    user_name: str
    
    class Config:
        alias_generator = to_camel  # Helper function

# JSON output
{
  "createdAt": "2025-12-16T12:00:00Z",
  "userName": "Alice"
}
```

Frontend TypeScript interfaces mirror the camelCase format directly.

**Data model complete. All entities, relationships, and validation rules defined. Ready for contract generation.**
