# Tasks: MySQL Support

**Input**: Design documents from `/specs/002-mysql-support/`
**Prerequisites**: plan.md, spec.md
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Web app structure: `backend/src/`, `frontend/src/`
- Tests: `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add MySQL client library and update project configuration

- [x] T001 Add mysql-connector-python dependency to backend/pyproject.toml
- [x] T002 Install MySQL dependencies using package manager
- [x] T003 Create test MySQL connection script to verify local myapp1 database access

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extend core data models to support multiple database types

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Add database_type field to DatabaseConnection model in backend/src/models/database.py
- [x] T005 Update SQLite schema to add database_type column with default 'postgresql' for backward compatibility
- [x] T006 Update storage service to persist and retrieve database_type in backend/src/services/storage.py
- [x] T007 Add database type detection utility function in backend/src/services/db_connection.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - MySQL Database Connection & Metadata Extraction (Priority: P1) 🎯 MVP

**Goal**: Enable users to connect to MySQL databases and view schema structure (tables, views, columns)

**Independent Test**: Add MySQL connection URL (mysql://root@localhost/myapp1), verify connection succeeds, metadata extraction completes, and MySQL tables appear in UI. Test with: `mysql -u root -e "SELECT * FROM myapp1.todos;"`

### Implementation for User Story 1

- [x] T008 [US1] Implement MySQL connection URL parsing in backend/src/services/db_connection.py
- [x] T009 [US1] Implement test_mysql_connection() method in backend/src/services/db_connection.py
- [x] T010 [US1] Implement get_mysql_connection() context manager in backend/src/services/db_connection.py
- [x] T011 [US1] Add MySQL metadata extraction method _extract_mysql_tables_and_views() in backend/src/services/metadata_extractor.py
- [x] T012 [US1] Add MySQL column metadata extraction method _extract_mysql_columns() in backend/src/services/metadata_extractor.py
- [x] T013 [US1] Add MySQL row count retrieval method _get_mysql_row_count() in backend/src/services/metadata_extractor.py
- [x] T014 [US1] Update extract_metadata() to route to MySQL or PostgreSQL based on database_type in backend/src/services/metadata_extractor.py
- [x] T015 [US1] Update POST /api/v1/databases/ endpoint to detect database type from URL in backend/src/api/v1/databases.py
- [x] T016 [US1] Update GET /api/v1/databases/ endpoint to return database_type in response in backend/src/api/v1/databases.py
- [x] T017 [US1] Update GET /api/v1/databases/{db_name}/metadata/ to handle MySQL metadata in backend/src/api/v1/databases.py
- [x] T018 [US1] Add error handling for MySQL-specific connection errors in backend/src/services/db_connection.py
- [x] T019 [US1] Add validation for MySQL connection URL format in backend/src/models/database.py

**Checkpoint**: At this point, User Story 1 should be fully functional - can connect to MySQL and view schema independently

---

## Phase 4: User Story 2 - MySQL SQL Query Execution (Priority: P2)

**Goal**: Enable users to execute SELECT queries against MySQL databases with safety validation

**Independent Test**: Select MySQL database, enter SELECT query (e.g., "SELECT * FROM todos"), execute, verify results display in table format. Verify LIMIT 1000 auto-applied and non-SELECT queries rejected.

### Implementation for User Story 2

- [x] T020 [US2] Add MySQL query execution support in execute_query() method in backend/src/services/query_executor.py
- [x] T021 [US2] Implement MySQL result set to JSON conversion handling MySQL data types (DATETIME, TINYINT, ENUM, JSON) in backend/src/services/query_executor.py
- [x] T022 [US2] Verify SQL validator handles MySQL dialect syntax (backticks, MySQL functions) in backend/src/utils/sql_validator.py
- [x] T023 [US2] Add MySQL-specific error handling and error message formatting in backend/src/services/query_executor.py
- [x] T024 [US2] Update POST /api/v1/databases/{db_name}/query/ to route to correct database type in backend/src/api/v1/queries.py
- [x] T025 [US2] Test LIMIT 1000 auto-append works correctly for MySQL queries in backend/src/services/query_executor.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - can connect and query MySQL databases

---

## Phase 5: User Story 3 - Natural Language to SQL for MySQL (Priority: P3)

**Goal**: Enable natural language query conversion to MySQL-compatible SQL syntax

**Independent Test**: Select MySQL database, enter natural language query (e.g., "show all todos from last week"), verify generated SQL uses MySQL syntax (NOW(), DATE_SUB(), backticks), execute successfully.

### Implementation for User Story 3

- [x] T026 [US3] Update convert_nl_to_sql() to accept database_type parameter in backend/src/services/nl_converter.py
- [x] T027 [US3] Modify LLM prompt to include explicit MySQL dialect instruction when database_type is mysql in backend/src/services/nl_converter.py
- [x] T028 [US3] Update schema context formatting to include MySQL-specific type information in backend/src/services/nl_converter.py
- [x] T029 [US3] Update POST /api/v1/databases/{db_name}/nl-query/ to pass database_type to nl_converter in backend/src/api/v1/queries.py
- [x] T030 [US3] Add validation that generated MySQL SQL follows MySQL syntax conventions in backend/src/services/nl_converter.py

**Checkpoint**: All user stories should now be independently functional - full MySQL support complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Testing, documentation, and validation across all user stories

- [x] T031 [P] Create unit tests for MySQL connection handling in backend/tests/test_mysql_connection.py
- [x] T032 [P] Create unit tests for MySQL metadata extraction in backend/tests/test_mysql_metadata_extractor.py
- [x] T033 [P] Create integration test for MySQL end-to-end workflow in backend/tests/test_mysql_e2e.py
- [x] T034 [P] Create test for natural language to MySQL SQL conversion in backend/tests/test_mysql_nl_query.py
- [x] T035 Run all existing PostgreSQL tests to ensure no regression
- [x] T036 Test simultaneous PostgreSQL and MySQL connections
- [x] T037 [P] Update README.md with MySQL support documentation
- [x] T038 [P] Create quickstart.md with MySQL testing scenarios in specs/002-mysql-support/
- [x] T039 Verify error messages are clear and actionable for MySQL-specific errors
- [x] T040 Performance testing: verify MySQL metadata extraction completes < 30 seconds for myapp1 database

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed sequentially (P1 → P2 → P3) or in parallel if multiple developers
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for database connectivity but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 for schema context and US2 for query execution, but should be independently testable

### Within Each User Story

**User Story 1** (Connection & Metadata):
- T008-T010: MySQL connection methods (can run in parallel)
- T011-T013: MySQL metadata extraction methods (can run in parallel after T008-T010)
- T014: Router method (depends on T011-T013)
- T015-T017: API endpoint updates (can run in parallel after T014)
- T018-T019: Error handling and validation (can run in parallel)

**User Story 2** (Query Execution):
- T020-T021: Query execution and result conversion (sequential)
- T022: SQL validator verification (parallel with T020-T021)
- T023-T025: Error handling, API routing, LIMIT testing (sequential after T020)

**User Story 3** (Natural Language):
- T026-T028: NL converter updates (sequential)
- T029-T030: API integration and validation (sequential after T026-T028)

### Parallel Opportunities

- **Phase 1** (Setup): T001, T002, T003 can run sequentially (dependencies on package install)
- **Phase 2** (Foundational): T004-T007 should run sequentially (model → schema → storage → utility)
- **Within US1**: T008-T010 parallel, T011-T013 parallel, T015-T017 parallel, T018-T019 parallel
- **Within US2**: T022 parallel with T020-T021
- **Phase 6** (Polish): T031-T034 parallel, T037-T038 parallel

---

## Parallel Example: User Story 1

```bash
# Parallel batch 1 - MySQL connection methods:
Task T008: "Implement MySQL connection URL parsing"
Task T009: "Implement test_mysql_connection() method"
Task T010: "Implement get_mysql_connection() context manager"

# Parallel batch 2 - MySQL metadata extraction methods:
Task T011: "Add MySQL metadata extraction method _extract_mysql_tables_and_views()"
Task T012: "Add MySQL column metadata extraction method _extract_mysql_columns()"
Task T013: "Add MySQL row count retrieval method _get_mysql_row_count()"

# Parallel batch 3 - API endpoint updates:
Task T015: "Update POST /api/v1/databases/ endpoint to detect database type"
Task T016: "Update GET /api/v1/databases/ endpoint to return database_type"
Task T017: "Update GET /api/v1/databases/{db_name}/metadata/ to handle MySQL"

# Parallel batch 4 - Error handling and validation:
Task T018: "Add error handling for MySQL-specific connection errors"
Task T019: "Add validation for MySQL connection URL format"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (add MySQL dependencies)
2. Complete Phase 2: Foundational (extend data models)
3. Complete Phase 3: User Story 1 (connection + metadata)
4. **STOP and VALIDATE**: Test MySQL connection and metadata display
5. Can connect to myapp1, see todos table structure

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Can browse MySQL schema (MVP!)
3. Add User Story 2 → Test independently → Can query MySQL data
4. Add User Story 3 → Test independently → Can use natural language with MySQL
5. Complete Polish → All tests pass, documentation updated

### Testing Checkpoints

**After User Story 1**:
- [ ] Can add mysql://root@localhost/myapp1 connection
- [ ] Database appears in list with type "mysql"
- [ ] Tables from myapp1 appear in schema tree
- [ ] Clicking todos table shows column information

**After User Story 2**:
- [ ] Can execute: SELECT * FROM todos
- [ ] Results display in table format
- [ ] LIMIT 1000 auto-appended to unbounded queries
- [ ] Non-SELECT queries are rejected with clear error

**After User Story 3**:
- [ ] Can enter: "show all todos"
- [ ] System generates valid MySQL SELECT statement
- [ ] Generated SQL uses MySQL syntax (not PostgreSQL)
- [ ] Execution succeeds and shows results

**After Polish**:
- [ ] All new MySQL tests pass
- [ ] All existing PostgreSQL tests pass (no regression)
- [ ] Can manage both PostgreSQL and MySQL connections simultaneously
- [ ] Documentation updated with MySQL examples

---

## Notes

- **Path Convention**: All backend code in `backend/src/`, tests in `backend/tests/`
- **No Frontend Changes**: Existing UI already handles database connections generically
- **Backward Compatibility**: Existing PostgreSQL connections continue working unchanged
- **Test Database**: Local `myapp1` MySQL database with `todos` table
- **Verification Command**: `mysql -u root -e "SELECT * FROM myapp1.todos;"`
- **Library Choice**: mysql-connector-python (official Oracle library, better type hints)
- **MySQL Versions**: Support MySQL 5.7+ and 8.0+
- **Validation**: Same constraints as PostgreSQL (SELECT-only, auto-LIMIT 1000)
