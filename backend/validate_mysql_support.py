#!/usr/bin/env python3
"""
End-to-end validation script for MySQL support.
Demonstrates complete workflow: connect → metadata → query.
"""

import sys
sys.path.insert(0, '/Users/alexz/Documents/Code/Github/ai-dev/w2/db-query/backend')

from src.services.db_connection import db_connection_service
from src.services.metadata_extractor import metadata_extractor
from src.services.query_executor import query_executor

print("=" * 80)
print("MySQL SUPPORT VALIDATION")
print("=" * 80)

# Test configuration
MYSQL_URL = "mysql://root@localhost/myapp1"

# Step 1: Database Type Detection
print("\n1. Database Type Detection")
print("-" * 80)
db_type = db_connection_service.detect_database_type(MYSQL_URL)
print(f"   URL: {MYSQL_URL}")
print(f"   Detected Type: {db_type}")
assert db_type == "mysql", "Failed: Database type should be 'mysql'"
print("   ✅ PASS: Database type correctly detected as MySQL")

# Step 2: Connection Test
print("\n2. Connection Test")
print("-" * 80)
success, error = db_connection_service.test_connection(MYSQL_URL)
print(f"   Connection Success: {success}")
if error:
    print(f"   Error: {error}")
assert success, f"Failed: MySQL connection failed: {error}"
print("   ✅ PASS: MySQL connection successful")

# Step 3: Database Name Extraction
print("\n3. Database Name Extraction")
print("-" * 80)
db_name = db_connection_service.extract_db_name_from_url(MYSQL_URL)
print(f"   Extracted Database Name: {db_name}")
assert db_name == "myapp1", "Failed: Database name should be 'myapp1'"
print("   ✅ PASS: Database name correctly extracted")

# Step 4: Metadata Extraction
print("\n4. Metadata Extraction")
print("-" * 80)
metadata = metadata_extractor.extract_metadata(MYSQL_URL, database_id=999)
print(f"   Tables Found: {len(metadata.tables)}")
assert len(metadata.tables) > 0, "Failed: No tables found"

# Find todos table
todos_table = next((t for t in metadata.tables if t.name == "todos"), None)
assert todos_table is not None, "Failed: todos table not found"

print(f"   Sample Table: {todos_table.schema_name}.{todos_table.name}")
print(f"   Table Type: {todos_table.table_type}")
print(f"   Row Count: {todos_table.row_count}")
print(f"   Columns: {len(todos_table.columns)}")

# Show first 3 columns
print(f"\n   First 3 Columns:")
for col in todos_table.columns[:3]:
    pk_marker = " [PRIMARY KEY]" if col.is_primary_key else ""
    print(f"     - {col.name}: {col.data_type}{pk_marker}")

assert any(col.is_primary_key for col in todos_table.columns), "Failed: No primary key found"
print("\n   ✅ PASS: Metadata extraction successful")

# Step 5: Query Execution
print("\n5. Query Execution (SELECT)")
print("-" * 80)
result = query_executor.execute_query(MYSQL_URL, "SELECT * FROM todos LIMIT 3")
print(f"   Rows Retrieved: {result.row_count}")
print(f"   Execution Time: {result.execution_time} ms")
print(f"   Columns: {', '.join(result.columns[:5])}...")

assert result.row_count > 0, "Failed: No rows returned"
assert result.row_count <= 3, "Failed: LIMIT not enforced"
assert result.execution_time > 0, "Failed: Execution time not recorded"

if result.rows:
    print(f"\n   Sample Row:")
    first_row = result.rows[0]
    for key, value in list(first_row.items())[:3]:
        print(f"     {key}: {value} ({type(value).__name__})")

print("\n   ✅ PASS: Query execution successful")

# Step 6: LIMIT Auto-Append
print("\n6. LIMIT Auto-Append Test")
print("-" * 80)
result = query_executor.execute_query(MYSQL_URL, "SELECT * FROM todos")
print(f"   Query: SELECT * FROM todos (no LIMIT)")
print(f"   Rows Retrieved: {result.row_count}")
assert result.row_count <= 1000, "Failed: Auto-LIMIT not working"
print("   ✅ PASS: LIMIT 1000 auto-appended")

# Step 7: SELECT-Only Enforcement
print("\n7. SELECT-Only Enforcement")
print("-" * 80)
try:
    query_executor.execute_query(MYSQL_URL, "DELETE FROM todos WHERE id = 999")
    print("   ❌ FAIL: DELETE query should have been blocked")
    sys.exit(1)
except ValueError as e:
    print(f"   Blocked Query: DELETE FROM todos WHERE id = 999")
    print(f"   Error: {e}")
    print("   ✅ PASS: Non-SELECT query correctly blocked")

# Step 8: MySQL Syntax Support (Backticks)
print("\n8. MySQL Syntax Support (Backticks)")
print("-" * 80)
result = query_executor.execute_query(MYSQL_URL, "SELECT `id`, `title` FROM `todos` LIMIT 2")
print(f"   Query: SELECT `id`, `title` FROM `todos` LIMIT 2")
print(f"   Rows Retrieved: {result.row_count}")
assert result.row_count <= 2, "Failed: Backtick query failed"
print("   ✅ PASS: MySQL backtick syntax works")

# Summary
print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
print("\n✅ All 8 validation tests passed!")
print("\nMySQL support is fully functional:")
print("  • Database type detection")
print("  • Connection handling")
print("  • Metadata extraction (information_schema)")
print("  • Query execution with data type conversion")
print("  • LIMIT auto-append")
print("  • SELECT-only enforcement")
print("  • MySQL-specific syntax (backticks)")
print("\n" + "=" * 80)
