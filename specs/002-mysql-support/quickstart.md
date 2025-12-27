# Quickstart: MySQL Support Testing

**Feature**: MySQL database support for query tool  
**Branch**: `002-mysql-support`  
**Prerequisites**: Local MySQL server running with `myapp1` database

## Prerequisites

### Verify MySQL Database Access

```bash
# Test MySQL connection and verify myapp1 database exists
mysql -u root -e "SHOW DATABASES;" | grep myapp1

# Verify todos table exists and has data
mysql -u root -e "SELECT * FROM myapp1.todos;"

# Expected output: List of todos with columns
```

### Environment Setup

```bash
# Ensure backend dependencies are installed
cd backend
# Install mysql-connector-python
# poetry install or pip install mysql-connector-python

# Set OpenAI API key (for natural language queries)
export OPENAI_API_KEY="your-api-key-here"
```

## Testing Scenarios

### Scenario 1: MySQL Connection & Metadata Extraction (User Story 1)

**Goal**: Verify MySQL database connection and schema browsing

**Steps**:

1. **Start the backend server**:
   ```bash
   cd backend
   # uvicorn src.main:app --reload
   # or make run
   ```

2. **Add MySQL database connection**:
   ```bash
   # POST request to add MySQL database
   curl -X POST http://localhost:8000/api/v1/databases/ \
     -H "Content-Type: application/json" \
     -d '{"url": "mysql://root@localhost/myapp1"}'
   ```

3. **Expected Response**:
   ```json
   {
     "id": 1,
     "name": "myapp1",
     "url": "mysql://root@localhost/myapp1",
     "databaseType": "mysql",
     "status": "connected",
     "lastConnected": "2025-12-25T..."
   }
   ```

4. **Verify database list includes MySQL**:
   ```bash
   curl http://localhost:8000/api/v1/databases/
   ```

5. **Expected Response**:
   ```json
   [
     {
       "id": 1,
       "name": "myapp1",
       "databaseType": "mysql",
       ...
     }
   ]
   ```

6. **Get MySQL metadata**:
   ```bash
   curl http://localhost:8000/api/v1/databases/myapp1/metadata/
   ```

7. **Expected Response** (partial):
   ```json
   {
     "databaseId": 1,
     "tables": [
       {
         "name": "todos",
         "schemaName": "myapp1",
         "tableType": "table",
         "columns": [
           {
             "name": "id",
             "dataType": "int",
             "isNullable": false,
             "isPrimaryKey": true
           },
           {
             "name": "title",
             "dataType": "varchar",
             "isNullable": true
           },
           {
             "name": "completed",
             "dataType": "tinyint",
             "isNullable": true
           }
         ],
         "rowCount": 5
       }
     ],
     "extractedAt": "2025-12-25T..."
   }
   ```

**Success Criteria**:
- ✅ MySQL connection succeeds
- ✅ Database type is "mysql"
- ✅ Tables from myapp1 database appear in metadata
- ✅ Columns show MySQL data types (int, varchar, tinyint, etc.)
- ✅ Row count is populated

---

### Scenario 2: MySQL Query Execution (User Story 2)

**Goal**: Verify SELECT query execution against MySQL database

**Steps**:

1. **Execute simple SELECT query**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT * FROM todos"}'
   ```

2. **Expected Response**:
   ```json
   {
     "columns": ["id", "title", "completed", "createdAt"],
     "rows": [
       {
         "id": 1,
         "title": "Buy groceries",
         "completed": false,
         "createdAt": "2025-12-20T10:00:00"
       },
       ...
     ],
     "rowCount": 5,
     "executionTime": 0.023
   }
   ```

3. **Test LIMIT auto-append**:
   ```bash
   # Query without LIMIT should auto-append LIMIT 1000
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT * FROM todos WHERE completed = 0"}'
   ```

4. **Test SELECT-only enforcement**:
   ```bash
   # Should REJECT non-SELECT queries
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "DELETE FROM todos WHERE id = 1"}'
   ```

5. **Expected Error Response**:
   ```json
   {
     "message": "Only SELECT statements are allowed",
     "code": "INVALID_SQL_STATEMENT",
     "details": "Query contains forbidden statement type: DELETE"
   }
   ```

6. **Test MySQL-specific syntax**:
   ```bash
   # MySQL backtick identifiers
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT `id`, `title` FROM `todos` WHERE `completed` = 0"}'
   ```

7. **Test MySQL functions**:
   ```bash
   # MySQL NOW() function
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT *, NOW() as current_time FROM todos LIMIT 5"}'
   ```

**Success Criteria**:
- ✅ SELECT queries execute successfully
- ✅ Results returned in JSON with camelCase keys
- ✅ LIMIT 1000 auto-appended when missing
- ✅ Non-SELECT queries are rejected
- ✅ MySQL backticks and functions work correctly
- ✅ MySQL data types converted properly (TINYINT → boolean, DATETIME → ISO string)

---

### Scenario 3: Natural Language to MySQL SQL (User Story 3)

**Goal**: Verify natural language query conversion generates MySQL-compatible SQL

**Steps**:

1. **Execute natural language query**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/nl-query/ \
     -H "Content-Type: application/json" \
     -d '{"nlQuery": "show all incomplete todos"}'
   ```

2. **Expected Response**:
   ```json
   {
     "generatedSql": "SELECT * FROM todos WHERE completed = 0 LIMIT 1000",
     "explanation": "Retrieve all todos where completed status is false",
     "results": {
       "columns": ["id", "title", "completed"],
       "rows": [...],
       "rowCount": 3
     }
   }
   ```

3. **Test MySQL-specific function generation**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/nl-query/ \
     -H "Content-Type: application/json" \
     -d '{"nlQuery": "show todos created today"}'
   ```

4. **Expected MySQL SQL** (should use MySQL date functions):
   ```sql
   SELECT * FROM todos 
   WHERE DATE(created_at) = CURDATE() 
   LIMIT 1000
   ```
   **NOT PostgreSQL syntax**: `WHERE DATE(created_at) = CURRENT_DATE`

5. **Test complex natural language**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/nl-query/ \
     -H "Content-Type: application/json" \
     -d '{"nlQuery": "count how many todos are completed grouped by day"}'
   ```

6. **Expected MySQL SQL**:
   ```sql
   SELECT DATE(created_at) as day, COUNT(*) as total 
   FROM todos 
   WHERE completed = 1 
   GROUP BY DATE(created_at)
   LIMIT 1000
   ```

**Success Criteria**:
- ✅ Natural language converts to valid MySQL SQL
- ✅ Generated SQL uses MySQL functions (CURDATE(), DATE(), NOW(), etc.)
- ✅ Generated SQL does NOT use PostgreSQL-specific syntax
- ✅ Generated SQL includes backticks for identifiers if appropriate
- ✅ Query executes successfully
- ✅ Results returned correctly

---

## Regression Testing: PostgreSQL Compatibility

**Goal**: Ensure MySQL support does not break existing PostgreSQL functionality

**Steps**:

1. **Add PostgreSQL database** (if available):
   ```bash
   curl -X POST http://localhost:8000/api/v1/databases/ \
     -H "Content-Type: application/json" \
     -d '{"url": "postgresql://user:pass@localhost/testdb"}'
   ```

2. **List databases**:
   ```bash
   curl http://localhost:8000/api/v1/databases/
   ```

3. **Expected Response** (both databases):
   ```json
   [
     {
       "id": 1,
       "name": "myapp1",
       "databaseType": "mysql",
       ...
     },
     {
       "id": 2,
       "name": "testdb",
       "databaseType": "postgresql",
       ...
     }
   ]
   ```

4. **Execute PostgreSQL query**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/databases/testdb/query/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT * FROM users LIMIT 10"}'
   ```

5. **Execute MySQL query**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT * FROM todos LIMIT 10"}'
   ```

**Success Criteria**:
- ✅ Can manage both PostgreSQL and MySQL connections simultaneously
- ✅ PostgreSQL queries still work correctly
- ✅ MySQL queries work correctly
- ✅ No cross-contamination of database types
- ✅ Database type correctly identified in all responses

---

## Edge Case Testing

### Invalid MySQL Connection URL

```bash
curl -X POST http://localhost:8000/api/v1/databases/ \
  -H "Content-Type: application/json" \
  -d '{"url": "mysql://root@localhost/nonexistent_db"}'
```

**Expected**: Error response with clear message about database not found

### MySQL Syntax Error

```bash
curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELCT * FROM todos"}'
```

**Expected**: Error response indicating syntax error near "SELCT"

### MySQL Connection Timeout

```bash
curl -X POST http://localhost:8000/api/v1/databases/ \
  -H "Content-Type: application/json" \
  -d '{"url": "mysql://root@unreachable-host:3306/myapp1"}'
```

**Expected**: Error response indicating connection timeout

---

## Frontend Testing (Manual)

If frontend is available:

1. **Open application in browser**: `http://localhost:3000`
2. **Add MySQL connection**: Click "Add Database", enter `mysql://root@localhost/myapp1`
3. **Verify database appears** in left sidebar with MySQL icon/indicator
4. **Click on myapp1** database to expand
5. **Verify todos table** appears in tree
6. **Click on todos table** to see columns in right panel
7. **Verify column types** show MySQL types (int, varchar, tinyint, etc.)
8. **Type SELECT query** in SQL editor: `SELECT * FROM todos`
9. **Click Execute** button
10. **Verify results** appear in table below editor
11. **Switch to natural language tab**
12. **Enter**: "show all incomplete todos"
13. **Click Generate SQL** button
14. **Verify MySQL SQL** appears in editor
15. **Click Execute** to run generated query
16. **Verify results** appear correctly

---

## Performance Testing

### Metadata Extraction Time

```bash
# Time the metadata extraction
time curl http://localhost:8000/api/v1/databases/myapp1/metadata/
```

**Success Criterion**: Should complete in < 30 seconds (typically < 5 seconds for small database)

### Query Execution Time

```bash
# Time a simple query
time curl -X POST http://localhost:8000/api/v1/databases/myapp1/query/ \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM todos LIMIT 1000"}'
```

**Success Criterion**: Should complete in < 5 seconds (excluding database latency)

---

## Cleanup

```bash
# Remove test database connection (optional)
curl -X DELETE http://localhost:8000/api/v1/databases/myapp1/

# Verify removal
curl http://localhost:8000/api/v1/databases/
```

---

## Summary Checklist

After completing all scenarios, verify:

- [ ] Can connect to MySQL database
- [ ] MySQL metadata extraction works
- [ ] MySQL tables and columns display correctly
- [ ] Can execute SELECT queries on MySQL
- [ ] LIMIT 1000 auto-appended
- [ ] Non-SELECT queries rejected
- [ ] MySQL syntax (backticks, functions) works
- [ ] Natural language generates MySQL SQL
- [ ] Generated SQL uses MySQL functions (not PostgreSQL)
- [ ] PostgreSQL functionality still works (no regression)
- [ ] Can manage both PostgreSQL and MySQL simultaneously
- [ ] Error messages are clear and helpful
- [ ] Performance meets targets (< 30s metadata, < 5s queries)

**All checkboxes should be ✅ before considering feature complete.**
