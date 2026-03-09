# Pytest configuration and fixtures for backend tests

import pytest
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Load test environment variables
load_dotenv()

# Configure pytest-asyncio
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_service():
    """Fixture to provide a database service instance for tests"""
    # Import based on DATABASE_URL
    db_url = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL"))
    
    if not db_url:
        pytest.skip("No database URL configured for tests")
    
    # Use SQLite service for sqlite URLs
    if db_url.startswith("sqlite"):
        from backend.database_sqlite import DatabaseService
    else:
        from backend.database import DatabaseService
    
    db = DatabaseService(db_url)
    await db.init_db()
    
    yield db
    
    # Cleanup: close connection pool if it exists
    if hasattr(db, 'pool') and db.pool:
        await db.pool.close()


@pytest.fixture
async def test_session(db_service):
    """Fixture to create a test session and clean it up after test"""
    session_id = await db_service.create_session("en")
    
    yield session_id
    
    # Cleanup: delete test session
    try:
        await db_service.delete_session(session_id)
    except:
        pass  # Session might already be deleted by test
