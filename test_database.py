#!/usr/bin/env python3
"""
Test Supabase database connection
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file")
    print("\nRun: python setup_database_url.py")
    sys.exit(1)

print(f"✓ Found DATABASE_URL")
print(f"  Host: {DATABASE_URL.split('@')[1].split(':')[0] if '@' in DATABASE_URL else 'unknown'}")

async def test_connection():
    try:
        import asyncpg
        
        print("\nTesting database connection...")
        
        # Try to connect
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("✅ Connected to database successfully!")
        
        # Test a simple query
        version = await conn.fetchval('SELECT version()')
        print(f"\n✓ PostgreSQL version: {version.split(',')[0]}")
        
        # Test creating a table
        print("\nTesting table creation...")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)
        print("✓ Test table created successfully")
        
        # Insert test data
        await conn.execute("""
            INSERT INTO test_table (name) VALUES ('test')
        """)
        print("✓ Test data inserted successfully")
        
        # Query test data
        count = await conn.fetchval('SELECT COUNT(*) FROM test_table')
        print(f"✓ Test table has {count} row(s)")
        
        # Clean up test table
        await conn.execute('DROP TABLE test_table')
        print("✓ Test table cleaned up")
        
        await conn.close()
        
        print("\n" + "="*60)
        print("✅ Database connection test PASSED!")
        print("Your Supabase database is ready to use.")
        print("="*60)
        
    except ImportError:
        print("\n❌ ERROR: asyncpg package not installed")
        print("\nInstall it with:")
        print("pip install asyncpg")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR: Database connection failed")
        print(f"\nError details: {str(e)}")
        print("\nPossible issues:")
        print("1. Wrong connection string - check your DATABASE_URL in .env")
        print("2. Wrong password - make sure you replaced [YOUR-PASSWORD]")
        print("3. Network issues - check your internet connection")
        print("4. Supabase project not ready - wait a few minutes and try again")
        sys.exit(1)

# Run the test
asyncio.run(test_connection())
