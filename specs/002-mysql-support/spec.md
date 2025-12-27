# Feature Specification: MySQL Support

**Feature Branch**: `002-mysql-support`  
**Created**: 2025-12-25  
**Status**: Draft  
**Input**: Add MySQL database support to existing PostgreSQL-only query tool. Reference ./backend/ Postgres implementation for patterns.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - MySQL Database Connection & Metadata Extraction (Priority: P1)

Users need to connect to MySQL databases in addition to PostgreSQL, and view MySQL database structure (tables, views, columns). This extends the tool's database support beyond PostgreSQL.

**Why this priority**: Extends core functionality to support MySQL. Users with MySQL databases currently cannot use the tool at all. This is foundational for all MySQL operations.

**Independent Test**: Can be fully tested by providing a valid MySQL connection URL (e.g., `mysql://root@localhost/myapp1`), verifying successful connection, and confirming that MySQL table/view names appear in the UI alongside any existing PostgreSQL connections. Test with local `myapp1` database using `mysql -u root -e "SELECT * FROM myapp1.todos;"` to verify connectivity.

**Acceptance Scenarios**:

1. **Given** user has no databases connected, **When** user enters a valid MySQL connection URL (format: `mysql://user:pass@host:port/dbname`) and submits, **Then** system detects MySQL protocol, connects using MySQL client, extracts metadata using `information_schema` queries, stores it in local SQLite, and displays database structure in left sidebar tree
2. **Given** user enters an invalid MySQL connection URL, **When** user submits the connection form, **Then** system displays clear error message indicating MySQL connection failure with specific reason (e.g., "Access denied", "Unknown database")
3. **Given** user has previously connected to a MySQL database, **When** user reopens the application, **Then** system loads cached MySQL metadata from SQLite without re-querying the MySQL database
4. **Given** user selects a MySQL table from the sidebar tree, **When** the table is clicked, **Then** system displays column information (name, data type in MySQL format) in the right panel
5. **Given** user has both PostgreSQL and MySQL databases connected, **When** user views the database list, **Then** system clearly indicates database type (PostgreSQL vs MySQL) for each connection

---

### User Story 2 - MySQL SQL Query Execution (Priority: P2)

Users need to write and execute SELECT queries against their connected MySQL databases, with the same safety validation and LIMIT enforcement as PostgreSQL queries.

**Why this priority**: After connecting to MySQL (P1), users immediately need the ability to query MySQL data. This is the primary value proposition for MySQL support.

**Independent Test**: Can be tested by selecting a MySQL database, entering a SELECT query using MySQL syntax in the SQL editor, executing it, and verifying results appear in table format below. Works independently if MySQL connection (P1) is established.

**Acceptance Scenarios**:

1. **Given** user has a MySQL database connected and selects a table, **When** user types a valid MySQL SELECT query in the SQL editor and clicks Execute, **Then** system validates the query, executes it against MySQL database, and displays results in JSON format rendered as a table
2. **Given** user enters a MySQL SELECT query without a LIMIT clause, **When** user executes the query, **Then** system automatically appends "LIMIT 1000" before execution and displays results
3. **Given** user enters a SQL query with MySQL-specific syntax (e.g., backtick identifiers, MySQL functions), **When** user executes the query, **Then** system correctly parses and executes the MySQL-dialect SQL
4. **Given** user enters a query containing UPDATE/DELETE/DROP statements on MySQL database, **When** user attempts to execute, **Then** system blocks execution and displays error message "Only SELECT statements are allowed"
5. **Given** a MySQL query is executing, **When** results are returned, **Then** system displays data in a formatted table with column headers, converting MySQL data types (DATETIME, TINYINT, etc.) to JSON-compatible formats

---

### User Story 3 - Natural Language to SQL for MySQL (Priority: P3)

Users need the ability to describe their MySQL query intent in natural language and have the system generate MySQL-compatible SQL syntax, using the same LLM integration as PostgreSQL but with MySQL schema context.

**Why this priority**: This is an enhancement that makes MySQL support feature-complete with PostgreSQL. The tool is fully functional without it (users can write MySQL SQL manually).

**Independent Test**: Can be tested by selecting a MySQL database, entering a natural language query like "show all todos from the last week", verifying MySQL-compatible SQL is generated (using MySQL date functions, syntax), and checking that the generated SQL executes successfully against MySQL.

**Acceptance Scenarios**:

1. **Given** user has a MySQL database connected with known schema, **When** user enters a natural language query (e.g., "find all records where status is active") in the designated input field, **Then** system sends MySQL schema metadata and user query to LLM with context that target database is MySQL, receives generated MySQL-compatible SQL, displays it in the SQL editor for review
2. **Given** LLM generates SQL with MySQL-specific syntax (e.g., backticks, MySQL functions like `NOW()`, `DATE_ADD()`), **When** user clicks Execute, **Then** system validates and executes the MySQL SQL following the same validation rules (SELECT-only, auto-LIMIT)
3. **Given** user switches from PostgreSQL to MySQL database, **When** natural language query is submitted, **Then** system generates SQL appropriate for MySQL dialect (not PostgreSQL syntax)
4. **Given** LLM generates invalid MySQL SQL, **When** user attempts to execute, **Then** system displays validation errors specific to MySQL syntax and allows user to edit the SQL manually

---

### Edge Cases

- What happens when MySQL connection is lost mid-query? System should detect connection failure and display reconnection prompt without losing user's current query text, same as PostgreSQL.
- How does system differentiate between PostgreSQL and MySQL connection URLs? System should parse URL protocol (`postgresql://` vs `mysql://`) and route to appropriate connection handler.
- What happens when MySQL metadata extraction encounters non-standard character sets or collations? System should handle encoding properly and display metadata without corruption.
- How does system handle MySQL-specific data types (ENUM, SET, JSON) in metadata and query results? System should represent these types accurately in metadata display and convert to appropriate JSON representations in query results.
- What happens when user attempts to execute PostgreSQL-specific syntax on MySQL database? System should detect incompatibility and provide helpful error message suggesting MySQL equivalent syntax.
- How does system handle MySQL stored procedures or triggers in schema? System should list these in metadata but prevent execution (read-only constraint).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept MySQL connection URLs (format: `mysql://user:password@host:port/database`) and establish connections to MySQL databases
- **FR-002**: System MUST detect database type (PostgreSQL vs MySQL) from connection URL protocol
- **FR-003**: System MUST extract database metadata (tables, views, columns with MySQL data types) from connected MySQL databases using `information_schema` queries
- **FR-004**: System MUST store MySQL connection URLs and extracted metadata in local SQLite database with database type indicator
- **FR-005**: System MUST display MySQL database structure (tables and views) in the hierarchical tree interface in the left sidebar, with visual distinction from PostgreSQL databases
- **FR-006**: System MUST display detailed MySQL column information (name, MySQL data type, nullable, default value, primary key status) when user selects a MySQL table or view
- **FR-007**: System MUST validate all MySQL SQL queries using sqlparse before execution
- **FR-008**: System MUST reject any MySQL SQL statements other than SELECT (no INSERT, UPDATE, DELETE, DROP, ALTER, etc.)
- **FR-009**: System MUST automatically append "LIMIT 1000" to MySQL SELECT queries that do not contain a LIMIT clause
- **FR-010**: System MUST execute validated SELECT queries against the connected MySQL database using appropriate MySQL client library
- **FR-011**: System MUST convert MySQL query results to JSON format with camelCase field naming, handling MySQL-specific data types (DATETIME, TINYINT, ENUM, JSON, etc.)
- **FR-012**: System MUST display MySQL query results in the same formatted table view as PostgreSQL results
- **FR-013**: System MUST accept natural language query descriptions from users when MySQL database is selected
- **FR-014**: System MUST convert natural language queries to MySQL-compatible SQL using LLM integration, providing MySQL schema context and explicitly indicating MySQL dialect
- **FR-015**: System MUST display LLM-generated MySQL SQL in the editor for user review before execution
- **FR-016**: System MUST validate LLM-generated MySQL SQL using the same rules as manually written queries
- **FR-017**: System MUST provide clear, specific error messages for MySQL connection failures, syntax errors, and validation failures
- **FR-018**: System MUST support multiple simultaneous connections to both PostgreSQL and MySQL databases
- **FR-019**: System MUST persist MySQL connections and metadata in SQLite, loading cached data on application startup
- **FR-020**: System MUST provide mechanism to refresh MySQL metadata when database schema changes

### Key Entities *(include if feature involves data)*

- **Database Connection (Extended)**: Existing entity extended with `database_type` field to distinguish between "postgresql" and "mysql". Attributes include connection URL, connection name/identifier, database type, connection status, last connected timestamp. Stored in SQLite.

- **Table Metadata (MySQL-aware)**: Existing entity works with MySQL but requires MySQL-specific metadata extraction queries. MySQL data types (VARCHAR, INT, DATETIME, ENUM, SET, JSON, TINYINT, etc.) must be properly extracted and displayed.

- **Column Metadata (MySQL data types)**: Existing entity must handle MySQL-specific data types and constraints. MySQL uses different type names than PostgreSQL (e.g., `INT` vs `INTEGER`, `DATETIME` vs `TIMESTAMP`, backtick identifiers).

### Non-Functional Requirements

- **NFR-001**: MySQL metadata extraction should complete within 30 seconds for databases with < 1000 tables
- **NFR-002**: MySQL connection establishment should complete within 5 seconds
- **NFR-003**: MySQL query execution performance should match PostgreSQL performance (< 5 seconds excluding database latency)
- **NFR-004**: System must maintain same security constraints for MySQL (read-only SELECT access)
- **NFR-005**: Error messages for MySQL operations should be as clear and actionable as PostgreSQL error messages

## Technical Constraints

- **TC-001**: Use `mysql-connector-python` or `PyMySQL` library for MySQL connections (select based on compatibility and feature set)
- **TC-002**: MySQL metadata extraction must use `information_schema` database (ANSI SQL standard, available in all MySQL 5.0+ versions)
- **TC-003**: MySQL connection URLs must follow standard format: `mysql://username:password@hostname:port/database`
- **TC-004**: System must support MySQL 5.7+ and MySQL 8.0+ (current widely-used versions)
- **TC-005**: MySQL-specific syntax validation should use sqlparse or SQLGlot with MySQL dialect support
- **TC-006**: Natural language to SQL conversion must explicitly inform LLM of MySQL dialect to ensure correct syntax generation

## Success Criteria

1. User can successfully connect to MySQL database using connection URL
2. MySQL database tables and views appear in schema tree
3. MySQL column metadata displays correctly with MySQL-specific data types
4. User can execute SELECT queries against MySQL database
5. Query results display correctly in table format
6. System enforces SELECT-only and LIMIT constraints for MySQL
7. Natural language queries generate valid MySQL-compatible SQL
8. User can have both PostgreSQL and MySQL databases connected simultaneously
9. No regression in existing PostgreSQL functionality
