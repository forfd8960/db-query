# Implementation Plan: MySQL Support

**Branch**: `002-mysql-support` | **Date**: 2025-12-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-mysql-support/spec.md`

## Summary

Extend the existing PostgreSQL-only database query tool to support MySQL databases. Users will be able to connect to MySQL databases using standard MySQL connection URLs, browse MySQL schema metadata (tables/views/columns), execute SQL queries with the same safety validation (SELECT-only, auto-LIMIT 1000), and convert natural language to MySQL-compatible SQL using LLM. The implementation will follow the existing PostgreSQL patterns in `./backend/`, adapting metadata extraction to use MySQL's `information_schema` and adding MySQL-specific connection handling.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ with strict mode (frontend) - **NO CHANGES**  
**Primary Dependencies**: 
- Backend (NEW): mysql-connector-python or PyMySQL (select based on compatibility)
- Backend (EXISTING): FastAPI, Pydantic, sqlparse, SQLGlot, OpenAI SDK, psycopg2, SQLite
- Frontend (EXISTING): React 19+, Refine 5, Ant Design, Tailwind CSS 4, Monaco Editor - **NO FRONTEND CHANGES REQUIRED** (UI already handles database connections generically)

**Storage**: SQLite (extend existing schema to include `database_type` field); MySQL (external, user-provided databases for querying)  
**Testing**: pytest (backend) - add MySQL-specific test cases  
**Target Platform**: Web application - **NO CHANGES**  
**Performance Goals**: 
- MySQL metadata extraction < 30 seconds for typical databases (< 1000 tables)
- MySQL query execution < 5 seconds (excluding database latency)
- Match PostgreSQL performance benchmarks

**Constraints**: 
- Read-only database access (SELECT only, enforced via sqlparse) - **SAME AS POSTGRESQL**
- Auto-LIMIT 1000 for unbounded queries - **SAME AS POSTGRESQL**
- Support MySQL 5.7+ and MySQL 8.0+
- No authentication (open access) - **NO CHANGES**
- Maintain backward compatibility with existing PostgreSQL functionality

**Scale/Scope**: 
- Single-user local application - **NO CHANGES**
- Support MySQL databases with < 1000 tables for optimal performance
- Multiple database connections (PostgreSQL + MySQL) managed simultaneously

## Constitution Check

*GATE: Must pass before implementation. Re-check after completion.*

### Principle I: Strict Type Safety ✅
- Backend: All new MySQL code will use type hints (enforced by mypy in development)
- Pydantic models extended with `database_type: Literal["postgresql", "mysql"]` field
- MySQL client library calls properly typed

**Status**: PASS - Extends existing type-safe architecture

### Principle II: Ergonomic Code Style ✅
- Backend: Follow same Ergonomic Python patterns as existing PostgreSQL implementation
- Code structure mirrors PostgreSQL services (metadata_extractor.py pattern)
- Clear separation of concerns (connection, metadata extraction, query execution)

**Status**: PASS - Follows established code patterns

### Principle III: Data Model Standards ✅
- Extend existing Pydantic models with minimal changes (add `database_type` field)
- Maintain camelCase serialization for API responses
- MySQL data types properly mapped to Python/JSON types

**Status**: PASS - Minimal model changes, consistent with existing patterns

### Principle IV: API Conventions ✅
- NO API endpoint changes required (existing endpoints already database-agnostic)
- Same REST conventions, JSON camelCase responses
- Error response format unchanged

**Status**: PASS - No API changes, maintains existing conventions

### Principle V: Open Access ✅
- No authentication changes
- MySQL connections use same open-access model as PostgreSQL

**Status**: PASS - No security model changes

### Overall Gate Result: ✅ PASS

All constitution principles satisfied. Implementation extends existing patterns without violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-mysql-support/
├── spec.md              # Feature specification
├── plan.md              # This file
├── tasks.md             # Generated task list (to be created)
└── quickstart.md        # Quick testing guide (to be created)
```

### Code Structure (Extensions to Existing)

```text
backend/src/
├── models/
│   ├── database.py      # EXTEND: Add database_type field to DatabaseConnection model
│   └── metadata.py      # NO CHANGES (already generic)
├── services/
│   ├── db_connection.py           # EXTEND: Add MySQL connection support
│   ├── metadata_extractor.py     # EXTEND: Add MySQL metadata extraction
│   ├── query_executor.py         # EXTEND: Add MySQL query execution
│   ├── nl_converter.py            # EXTEND: Add MySQL dialect context
│   └── storage.py                 # EXTEND: Store/retrieve database_type
└── api/v1/
    ├── databases.py     # MINOR CHANGES: Return database_type in responses
    └── queries.py       # NO CHANGES (already database-agnostic)
```

### Dependencies to Add

```text
# pyproject.toml [tool.poetry.dependencies]
mysql-connector-python = "^8.2.0"  # OR PyMySQL = "^1.1.0"
# Decision: mysql-connector-python (official Oracle library, better type hints)
```

## Implementation Strategy

### Phase 1: MySQL Connection Support

**Goal**: Enable system to connect to MySQL databases and differentiate from PostgreSQL

**Approach**:
1. Extend `DatabaseConnection` Pydantic model with `database_type` field
2. Update SQLite schema migration to add `database_type` column
3. Implement MySQL connection detection (parse URL protocol)
4. Add MySQL connection testing and management in `db_connection.py`
5. Update storage service to persist and retrieve `database_type`

**Key Files**:
- `backend/src/models/database.py` - Add `database_type: Literal["postgresql", "mysql"]`
- `backend/src/services/db_connection.py` - Add `get_mysql_connection()`, `test_mysql_connection()`
- `backend/src/services/storage.py` - Update CRUD operations to include `database_type`

**Test Criteria**: 
- Can add MySQL connection URL via API
- System correctly identifies database as MySQL
- MySQL connection test succeeds/fails appropriately
- Stored in SQLite with correct type

### Phase 2: MySQL Metadata Extraction

**Goal**: Extract table, view, and column metadata from MySQL databases using `information_schema`

**Approach**:
1. Research MySQL `information_schema` queries for tables, views, columns
2. Implement MySQL-specific metadata extraction methods in `metadata_extractor.py`
3. Handle MySQL-specific data types (INT, VARCHAR, DATETIME, ENUM, SET, JSON, TINYINT, etc.)
4. Ensure metadata extraction works with MySQL 5.7+ and 8.0+
5. Cache extracted MySQL metadata in SQLite

**Key Files**:
- `backend/src/services/metadata_extractor.py` - Add `_extract_mysql_tables_and_views()`, `_extract_mysql_columns()`

**MySQL-Specific Queries**:
```sql
-- Tables and Views
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
ORDER BY TABLE_SCHEMA, TABLE_NAME;

-- Columns
SELECT 
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_KEY
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
ORDER BY ORDINAL_POSITION;

-- Row Count (approximation)
SELECT TABLE_ROWS 
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;
```

**Test Criteria**:
- Can extract metadata from `myapp1` MySQL database
- Tables appear in API response with correct types
- Columns show MySQL data types accurately
- Row counts retrieved (approximate OK)

### Phase 3: MySQL Query Execution

**Goal**: Execute SELECT queries against MySQL databases with validation and safety constraints

**Approach**:
1. Extend `query_executor.py` to handle MySQL connections
2. Ensure sqlparse/SQLGlot validates MySQL syntax
3. Apply SELECT-only and LIMIT constraints to MySQL queries
4. Handle MySQL result set conversion to JSON (handle DATETIME, TINYINT → bool, etc.)
5. Proper error handling for MySQL-specific errors

**Key Files**:
- `backend/src/services/query_executor.py` - Add MySQL execution path
- `backend/src/utils/sql_validator.py` - Ensure MySQL dialect support

**Test Criteria**:
- Can execute SELECT queries on `myapp1.todos` table
- Results returned in JSON with camelCase
- LIMIT 1000 auto-applied when missing
- Non-SELECT queries rejected
- MySQL syntax errors caught and reported

### Phase 4: Natural Language to MySQL SQL

**Goal**: Generate MySQL-compatible SQL from natural language queries

**Approach**:
1. Extend `nl_converter.py` to include database type context
2. Pass MySQL schema metadata to LLM with explicit "MySQL dialect" instruction
3. Ensure LLM generates MySQL syntax (backticks, `NOW()`, `CONCAT()`, etc.)
4. Validate generated MySQL SQL before execution

**Key Files**:
- `backend/src/services/nl_converter.py` - Add database type awareness

**LLM Prompt Changes**:
```python
# Current (PostgreSQL assumed)
prompt = f"Generate SQL query for: {nl_query}\nSchema: {schema}"

# New (database type explicit)
prompt = f"Generate {db_type.upper()} SQL query for: {nl_query}\nSchema: {schema}\nUse {db_type.upper()} syntax and functions."
```

**Test Criteria**:
- Natural language query on MySQL generates valid MySQL SQL
- Generated SQL uses MySQL functions (not PostgreSQL equivalents)
- Generated SQL executes successfully

## Testing Strategy

### Unit Tests
- `test_mysql_connection.py` - MySQL connection establishment, URL parsing, error handling
- `test_mysql_metadata_extractor.py` - Metadata extraction from MySQL information_schema
- `test_mysql_query_executor.py` - Query validation and execution

### Integration Tests
- `test_mysql_e2e.py` - Full workflow: connect → extract metadata → execute query
- `test_mysql_nl_query.py` - Natural language to MySQL SQL conversion

### Test Data
- Use local `myapp1` MySQL database with `todos` table
- Verify with: `mysql -u root -e "SELECT * FROM myapp1.todos;"`

### Regression Tests
- Ensure existing PostgreSQL tests still pass
- Test simultaneous PostgreSQL + MySQL connections

## Risk Assessment

### High Risk
- **MySQL connection library compatibility**: mysql-connector-python vs PyMySQL
  - Mitigation: Choose mysql-connector-python (official, better maintained)
  
- **information_schema query differences**: MySQL vs PostgreSQL
  - Mitigation: Test with MySQL 5.7 and 8.0 to ensure compatibility

### Medium Risk
- **MySQL data type mapping**: ENUM, SET, JSON types may not map cleanly to JSON
  - Mitigation: Handle edge cases explicitly (ENUM → string, SET → string array, JSON → passthrough)

- **LLM generating PostgreSQL syntax for MySQL databases**: Model confusion
  - Mitigation: Explicit database type in prompt, validate with SQLGlot MySQL dialect

### Low Risk
- **API changes breaking frontend**: Minimal API changes
  - Mitigation: Extend models, don't break existing fields

## Migration Notes

### Database Schema Changes
```sql
-- SQLite migration: Add database_type column
ALTER TABLE database_connections ADD COLUMN database_type TEXT DEFAULT 'postgresql';
```

### Backward Compatibility
- Existing PostgreSQL connections automatically get `database_type='postgresql'` via default
- No breaking changes to API response format (new field is additive)

## Dependencies

### External Libraries
- `mysql-connector-python ^8.2.0` - Official MySQL client library

### Internal Dependencies
- Extends existing services (no new architectural patterns)
- Reuses existing Pydantic models with minimal extensions
- No frontend changes required

## Success Metrics

1. ✅ Can connect to MySQL database using connection URL
2. ✅ MySQL metadata extraction completes < 30 seconds
3. ✅ MySQL queries execute successfully
4. ✅ Natural language generates valid MySQL SQL
5. ✅ All existing PostgreSQL tests still pass
6. ✅ Can manage PostgreSQL + MySQL connections simultaneously
7. ✅ No performance degradation for PostgreSQL operations

## Open Questions

1. **Q**: Should we support MySQL-specific features like stored procedures?
   **A**: No - maintain read-only SELECT constraint. List procedures in metadata but don't execute.

2. **Q**: How to handle MySQL vs PostgreSQL SQL editor hints?
   **A**: Frontend Monaco editor can show SQL syntax generally. Dialect-specific hints are out of scope.

3. **Q**: Should we migrate existing PostgreSQL connections to new schema?
   **A**: Yes - add default `database_type='postgresql'` in migration. Existing data unaffected.
