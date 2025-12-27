# Research: Database Query Tool

**Purpose**: Document technology decisions, best practices, and implementation patterns for the database query tool.  
**Date**: 2025-12-16  
**Status**: Complete

## Overview

All technical context fully specified in plan.md - no NEEDS CLARIFICATION items remain. This document captures research on best practices, integration patterns, and decision rationale for the chosen technology stack.

## Technology Decisions

### Backend Stack

#### Decision: FastAPI + Pydantic
**Rationale**:
- FastAPI provides automatic OpenAPI schema generation from Pydantic models
- Native async support for concurrent database operations
- Excellent type hint integration (aligns with Constitution Principle I)
- Built-in request/response validation via Pydantic
- Easy CORS middleware configuration

**Best Practices**:
- Use dependency injection for database connections and services
- Separate API routes, business logic (services), and data models (Pydantic)
- Configure Pydantic to use `alias_generator=to_camel` for automatic camelCase serialization
- Use FastAPI's `HTTPException` with proper status codes (200, 400, 404, 500)

**Alternatives Considered**:
- Flask: Less modern, requires manual validation, no automatic OpenAPI
- Django: Too heavyweight for API-only backend, includes unnecessary ORM
- Rejected because FastAPI better supports type safety and modern Python patterns

#### Decision: sqlparse for SQL Validation
**Rationale**:
- Pure Python library, easy to integrate
- Can parse and identify SQL statement types (SELECT vs UPDATE/DELETE/DROP)
- Provides syntax error detection with line/column information
- Lightweight (no database engine required for parsing)

**Best Practices**:
- Parse SQL before execution to detect statement type
- Reject any non-SELECT statements (enforce read-only access)
- Use `sqlparse.format()` to detect and add missing LIMIT clauses
- Provide detailed error messages from parsing failures

**Alternatives Considered**:
- SQLGlot: More powerful but complex for simple validation needs
- psycopg2 execution errors: Too late (after sending to database)
- Kept both: sqlparse for validation, SQLGlot for potential query transformation

#### Decision: SQLite for Metadata Cache
**Rationale**:
- Built into Python standard library (zero external dependencies)
- Perfect for local single-user storage
- JSON column support for flexible metadata schemas
- Fast for read-heavy workloads (metadata retrieval)

**Best Practices**:
- Store connection URLs with encryption or warnings about sensitive data
- Use JSON columns for table/column metadata (flexible schema)
- Index by database name for fast lookup
- Implement cache invalidation when user requests metadata refresh

**Schema Design**:
```sql
CREATE TABLE database_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_connected_at TIMESTAMP
);

CREATE TABLE database_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    database_id INTEGER REFERENCES database_connections(id),
    tables_metadata TEXT,  -- JSON array of table objects
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Decision: OpenAI SDK for Natural Language to SQL
**Rationale**:
- Official SDK provides stable API access
- Supports streaming responses (future enhancement)
- Handles authentication and error retry logic
- GPT-4 excels at SQL generation tasks

**Best Practices**:
- Include database schema in system prompt (table names, column names, data types)
- Use few-shot examples for common query patterns
- Set temperature=0 for consistent SQL generation
- Validate generated SQL through same pipeline as manual queries
- Provide user with generated SQL for review before execution

**Prompt Template**:
```
System: You are a SQL expert. Generate PostgreSQL SELECT queries based on user requests.
Database schema:
- Table: users (id INTEGER, name TEXT, email TEXT, created_at TIMESTAMP)
- Table: orders (id INTEGER, user_id INTEGER, amount DECIMAL, order_date DATE)

User: {natural_language_query}
Assistant: [SQL query only, no explanation]
```

### Frontend Stack

#### Decision: React + TypeScript + Refine
**Rationale**:
- React: Industry standard, excellent ecosystem, component reusability
- TypeScript: Strict type safety (Constitution Principle I), better IDE support
- Refine 5: Data-heavy framework perfect for CRUD operations and tables
- Refine provides data provider abstraction for backend API integration

**Best Practices**:
- Enable `strict: true` in tsconfig.json
- Use functional components with hooks (no class components)
- Define TypeScript interfaces for all API responses
- Use Refine's `useTable` hook for query result display
- Use Refine's data providers for database CRUD operations

**Alternatives Considered**:
- Vue.js: Smaller ecosystem, team less familiar
- Angular: Too heavyweight, opinionated structure
- Plain React without Refine: Would require manual table/form logic

#### Decision: Ant Design for UI Components
**Rationale**:
- Enterprise-grade component library with excellent table support
- Tree component perfect for schema browser
- Form components for database connection management
- Consistent design system out of the box
- Good TypeScript support

**Best Practices**:
- Use `<Table>` component with pagination for query results
- Use `<Tree>` component with `onSelect` for schema navigation
- Use `<Form>` with validation for database connection inputs
- Customize theme via Tailwind where needed

#### Decision: Monaco Editor for SQL Editing
**Rationale**:
- Same editor as VS Code (familiar to developers)
- Built-in SQL syntax highlighting
- Autocomplete support (can be extended with schema hints)
- Error highlighting for syntax errors

**Best Practices**:
- Configure `language: "sql"` for syntax highlighting
- Use `onChange` to capture query text
- Optionally add schema-based autocomplete (table/column names)
- Integrate with sqlparse validation to show errors inline

**Integration Pattern**:
```tsx
import Editor from '@monaco-editor/react';

<Editor
  height="200px"
  language="sql"
  theme="vs-dark"
  value={sqlQuery}
  onChange={(value) => setSqlQuery(value || '')}
  options={{
    minimap: { enabled: false },
    fontSize: 14,
  }}
/>
```

#### Decision: Tailwind CSS for Styling
**Rationale**:
- Utility-first approach reduces CSS overhead
- Excellent for responsive layouts
- Works well alongside Ant Design for custom components
- Fast development with no CSS file proliferation

**Best Practices**:
- Use Tailwind for layout (grid, flexbox, spacing)
- Use Ant Design for complex components (tables, forms, trees)
- Configure Tailwind to not conflict with Ant Design classes
- Use Tailwind's `@apply` for repeated utility combinations

### Integration Patterns

#### PostgreSQL Connection Management
**Pattern**: Connection pooling with async context managers

```python
from contextlib import asynccontextmanager
import psycopg2
from psycopg2 import pool

# Create connection pool per database
pools = {}

@asynccontextmanager
async def get_db_connection(db_name: str):
    if db_name not in pools:
        # Create pool from stored connection URL
        url = get_connection_url_from_sqlite(db_name)
        pools[db_name] = psycopg2.pool.SimpleConnectionPool(1, 10, url)
    
    conn = pools[db_name].getconn()
    try:
        yield conn
    finally:
        pools[db_name].putconn(conn)
```

**Rationale**: Reuse connections across requests, avoid connection overhead

#### Metadata Extraction Strategy
**Pattern**: Extract from PostgreSQL system catalogs, transform via LLM, cache in SQLite

```python
# Query PostgreSQL information_schema
metadata_query = """
SELECT 
    table_schema,
    table_name,
    table_type,
    column_name,
    data_type,
    is_nullable
FROM information_schema.tables t
JOIN information_schema.columns c USING (table_schema, table_name)
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_name, ordinal_position;
"""

# Transform to JSON structure
# LLM optional: can use direct JSON serialization
metadata_json = transform_to_json(results)

# Store in SQLite
store_metadata(db_name, metadata_json)
```

**Rationale**: System catalogs are standard PostgreSQL feature, JSON storage is flexible

#### SQL Validation Pipeline
**Pattern**: Multi-stage validation before execution

```python
def validate_and_execute_query(sql: str, db_name: str):
    # Stage 1: Parse SQL
    parsed = sqlparse.parse(sql)
    if not parsed:
        raise ValidationError("Invalid SQL syntax")
    
    # Stage 2: Check statement type
    stmt_type = parsed[0].get_type()
    if stmt_type != 'SELECT':
        raise ValidationError("Only SELECT statements allowed")
    
    # Stage 3: Add LIMIT if missing
    if 'LIMIT' not in sql.upper():
        sql = f"{sql.rstrip(';')} LIMIT 1000"
    
    # Stage 4: Execute
    results = execute_on_postgres(sql, db_name)
    return results
```

**Rationale**: Defense in depth, clear error messages, automatic safety enforcement

#### Frontend-Backend API Communication
**Pattern**: Typed API client with Refine data provider

```typescript
// types/api.ts
export interface Database {
  name: string;
  url: string;
  createdAt: string;
  lastConnectedAt?: string;
}

export interface QueryRequest {
  sql: string;
}

export interface QueryResult {
  columns: string[];
  rows: Record<string, any>[];
  rowCount: number;
}

// services/api.ts
const API_BASE = 'http://localhost:8000/api/v1';

export const databaseApi = {
  list: () => axios.get<Database[]>(`${API_BASE}/databases/`),
  create: (url: string) => axios.post(`${API_BASE}/databases/`, { url }),
  getMetadata: (dbName: string) => 
    axios.get(`${API_BASE}/databases/${dbName}/metadata/`),
  executeQuery: (dbName: string, sql: string) =>
    axios.post<QueryResult>(`${API_BASE}/databases/${dbName}/query/`, { sql }),
};
```

**Rationale**: Single source of truth for API types, type-safe calls, easy to test

## Security Considerations

### Open Access Model
**Decision**: No authentication (per Constitution Principle V)

**Implications**:
- Tool suitable only for development/internal use
- Users must understand security risks of storing connection URLs locally
- Backend should not be exposed to public internet

**Mitigations**:
- Document security limitations clearly in README
- Warn users about credential storage in SQLite
- Recommend using read-only PostgreSQL credentials
- Suggest network isolation (localhost only or VPN)

### SQL Injection Prevention
**Decision**: Use parameterized queries for SQLite, sqlparse validation for PostgreSQL

**Pattern**:
```python
# SQLite queries: parameterized
cursor.execute("SELECT * FROM connections WHERE name = ?", (db_name,))

# PostgreSQL queries: validate then execute
# User-provided SQL is not parameterized (user controls entire query)
# Instead, enforce read-only access via statement type checking
```

**Rationale**: User-provided SQL cannot be parameterized (defeats purpose), but validating statement type prevents destructive operations

### Sensitive Data Storage
**Decision**: Store PostgreSQL URLs in plaintext SQLite with user warnings

**Rationale**:
- Encryption adds complexity (key management, user passwords)
- Tool is for local development use
- Better solution: users should use environment variables or read-only credentials

**Recommendation**: Document best practices in quickstart.md

## Performance Optimizations

### Metadata Caching Strategy
- Extract once, cache in SQLite
- Serve from cache for all subsequent requests
- Provide manual refresh button for schema changes
- Expected speedup: 10-20x for repeated access

### Query Result Limiting
- Auto-LIMIT 1000 prevents memory overflow
- Frontend pagination if needed (future enhancement)
- Warn user if result set truncated

### Frontend Rendering
- Use React.memo for expensive components (table rendering)
- Virtualize long result tables (react-window if > 1000 rows)
- Debounce natural language input to reduce LLM API calls

## Testing Strategy

### Backend Testing
- Unit tests: Mock database connections, test validation logic
- Integration tests: Use test PostgreSQL database, verify metadata extraction
- Contract tests: Validate API responses match OpenAPI schema

### Frontend Testing
- Unit tests: Component rendering, user interactions (Vitest)
- Integration tests: API mocking, full user flows
- E2E tests: Optional (Playwright for critical paths)

## Development Workflow

### Backend Development
1. Start backend: `cd backend && uvicorn src.main:app --reload`
2. Access API docs: `http://localhost:8000/docs` (Swagger UI)
3. Run tests: `pytest tests/`

### Frontend Development
1. Start frontend: `cd frontend && npm run dev`
2. Access UI: `http://localhost:5173`
3. Run tests: `npm test`

### Environment Setup
- Backend: Python 3.11+ with uv/pip
- Frontend: Node.js 18+ with npm/yarn
- PostgreSQL: Test database for integration tests
- OpenAI API key: Set `OPENAI_API_KEY` environment variable

## Decisions Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Backend Framework | FastAPI | Type safety, async, auto-docs, Pydantic integration |
| Data Validation | Pydantic | Runtime validation, camelCase serialization, OpenAPI generation |
| SQL Validation | sqlparse | Statement type detection, syntax error reporting |
| SQL Transformation | SQLGlot | Advanced parsing (optional future use) |
| NL-to-SQL | OpenAI GPT-4 | State-of-art SQL generation |
| Metadata Storage | SQLite | Local, zero-config, JSON support |
| Frontend Framework | React + TypeScript | Type safety, component ecosystem |
| UI Library | Ant Design | Enterprise tables, trees, forms |
| SQL Editor | Monaco Editor | VS Code experience, syntax highlighting |
| Styling | Tailwind CSS | Utility-first, fast development |
| Data Framework | Refine 5 | CRUD abstractions, table management |

**All research complete. No NEEDS CLARIFICATION items remain. Ready for Phase 1: Design.**
