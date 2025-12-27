"""Test script for PostgreSQL database connection."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.db_connection import db_connection_service


def test_connection():
    """Test database connection."""
    # Database URL
    db_url = "postgres://postgres:postgres@localhost:5432/test_db"
    
    print(f"Testing connection to: {db_url}")
    print("-" * 60)
    
    # Test connection
    is_connected, error_msg = db_connection_service.test_connection(db_url)
    
    if is_connected:
        print("✅ Connection successful!")
        return True
    else:
        print(f"❌ Connection failed: {error_msg}")
        return False


def test_basic_operations():
    """Test basic database operations."""
    db_url = "postgresql://postgres:postgres@localhost:5432/test_db"
    
    print("\nTesting basic database operations...")
    print("-" * 60)
    
    try:
        with db_connection_service.get_connection(db_url) as conn:
            cursor = conn.cursor()
            
            # Create test table
            print("Creating test table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Table created")
            
            # Insert test data
            print("\nInserting test data...")
            cursor.execute("""
                INSERT INTO test_users (name, email) 
                VALUES ('Alice', 'alice@example.com'),
                       ('Bob', 'bob@example.com'),
                       ('Charlie', 'charlie@example.com')
            """)
            print("✅ Data inserted")
            
            # Query data
            print("\nQuerying data...")
            cursor.execute("SELECT id, name, email FROM test_users ORDER BY id")
            rows = cursor.fetchall()
            
            print(f"\nFound {len(rows)} rows:")
            for row in rows:
                print(f"  ID: {row[0]}, Name: {row[1]}, Email: {row[2]}")
            
            # Clean up
            print("\nCleaning up...")
            cursor.execute("DROP TABLE IF EXISTS test_users")
            print("✅ Table dropped")
            
            cursor.close()
            print("\n✅ All operations completed successfully!")
            return True
            
    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        return False


def test_metadata_extraction():
    """Test metadata extraction."""
    db_url = "postgresql://postgres:postgres@localhost:5432/test_db"
    
    print("\nTesting metadata extraction...")
    print("-" * 60)
    
    try:
        from src.services.metadata_extractor import metadata_extractor
        
        # Create a temporary table for testing
        with db_connection_service.get_connection(db_url) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_metadata (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.close()
        
        # Extract metadata (using connection_id=999 as a test)
        metadata = metadata_extractor.extract_metadata(db_url, 999)
        
        print(f"Database ID: {metadata.database_id}")
        print(f"Extracted at: {metadata.extracted_at}")
        print(f"\nTables found: {len(metadata.tables)}")
        
        for table in metadata.tables[:5]:  # Show first 5 tables
            print(f"\n  📋 {table.schema_name}.{table.name} ({table.table_type})")
            print(f"     Columns: {len(table.columns)}")
            print(f"     Rows: {table.row_count or 'N/A'}")
            for col in table.columns[:3]:  # Show first 3 columns
                pk = " [PK]" if col.is_primary_key else ""
                nullable = "NULL" if col.is_nullable else "NOT NULL"
                print(f"       - {col.name}: {col.data_type} {nullable}{pk}")
        
        # Clean up
        with db_connection_service.get_connection(db_url) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS test_metadata")
            cursor.close()
        
        print("\n✅ Metadata extraction successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Metadata extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("PostgreSQL Database Connection Tests")
    print("=" * 60)
    
    # Run tests
    results = []
    
    results.append(("Connection Test", test_connection()))
    results.append(("Basic Operations Test", test_basic_operations()))
    results.append(("Metadata Extraction Test", test_metadata_extraction()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
