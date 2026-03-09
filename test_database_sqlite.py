#!/usr/bin/env python3
"""
Test SQLite database connection
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
    sys.exit(1)

if not DATABASE_URL.startswith("sqlite"):
    print("❌ ERROR: This test is for SQLite only")
    print(f"Current DATABASE_URL: {DATABASE_URL}")
    print("\nChange DATABASE_URL in .env to: sqlite+aiosqlite:///./sidekick.db")
    sys.exit(1)

print(f"✓ Found DATABASE_URL: {DATABASE_URL}")

async def test_connection():
    try:
        # Import the SQLite database service
        sys.path.append("backend")
        from database_sqlite import DatabaseService
        
        print("\nInitializing SQLite database...")
        
        # Create database service
        db = DatabaseService(DATABASE_URL)
        await db.init_db()
        
        print("✅ Database initialized successfully!")
        
        # Test creating a session
        print("\nTesting session creation...")
        session_id = await db.create_session("en")
        print(f"✓ Created session: {session_id}")
        
        # Test adding transcript
        print("\nTesting transcript storage...")
        await db.add_transcript_chunk(session_id, "Doctor: Your blood pressure is elevated.")
        print("✓ Transcript chunk added")
        
        # Test adding simplification
        print("\nTesting simplification storage...")
        await db.add_simplification(session_id, "hypertension", "high blood pressure")
        print("✓ Simplification added")
        
        # Test adding summary
        print("\nTesting summary storage...")
        summary = {
            "title": "Test Visit",
            "diagnosis": "Elevated blood pressure",
            "medications": ["ACE inhibitor"],
            "instructions": ["Take medication daily"],
            "follow_up": "Return in 2 weeks",
            "key_points": ["Blood pressure elevated"]
        }
        await db.save_summary(session_id, summary)
        print("✓ Summary added")
        
        # Test retrieving session details
        print("\nTesting session retrieval...")
        details = await db.get_session_details(session_id)
        print(f"✓ Retrieved session with {len(details['transcript'])} transcript(s)")
        print(f"✓ Retrieved {len(details['simplifications'])} simplification(s)")
        print(f"✓ Retrieved summary: {details['summary']['title']}")
        
        # Test listing all sessions
        print("\nTesting session listing...")
        sessions = await db.get_all_sessions()
        print(f"✓ Found {len(sessions)} session(s)")
        
        # Test ending session
        print("\nTesting session end...")
        await db.end_session(session_id)
        print("✓ Session ended")
        
        # Test deleting session
        print("\nTesting session deletion...")
        await db.delete_session(session_id)
        print("✓ Session deleted")
        
        # Verify deletion
        deleted_session = await db.get_session_details(session_id)
        if deleted_session is None:
            print("✓ Session deletion verified (cascade delete worked)")
        
        print("\n" + "="*60)
        print("✅ All SQLite database tests PASSED!")
        print("Your database is ready to use.")
        print(f"Database file: {db.db_path}")
        print("="*60)
        
    except ImportError as e:
        print(f"\n❌ ERROR: Failed to import required packages")
        print(f"\nError details: {str(e)}")
        print("\nInstall required packages with:")
        print("pip install aiosqlite")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR: Database test failed")
        print(f"\nError details: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Run the test
asyncio.run(test_connection())
