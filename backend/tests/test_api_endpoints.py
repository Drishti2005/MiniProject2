# Unit tests for REST API endpoints

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_serve_frontend():
    """Test that frontend HTML is served at root"""
    response = client.get("/")
    assert response.status_code == 200
    # Should return HTML content
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_list_sessions_empty(db_service):
    """Test GET /api/sessions returns empty list initially"""
    response = client.get("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


@pytest.mark.asyncio
async def test_list_sessions_with_data(db_service):
    """Test GET /api/sessions returns sessions in correct format"""
    # Create a test session
    session_id = await db_service.create_session("en")
    
    response = client.get("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    
    assert "sessions" in data
    sessions = data["sessions"]
    assert len(sessions) > 0
    
    # Verify session structure
    session = sessions[0]
    assert "id" in session
    assert "title" in session
    assert "language" in session
    assert "created_at" in session
    
    # Cleanup
    await db_service.delete_session(session_id)


@pytest.mark.asyncio
async def test_get_session_valid_id(db_service):
    """Test GET /api/sessions/{id} with valid session ID"""
    # Create a test session with data
    session_id = await db_service.create_session("en")
    await db_service.add_transcript_chunk(session_id, "Test transcript")
    await db_service.add_simplification(session_id, "hypertension", "high blood pressure")
    
    response = client.get(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "session" in data
    assert "transcript" in data
    assert "simplifications" in data
    assert "summary" in data
    
    # Verify data
    assert data["session"]["id"] == session_id
    assert len(data["transcript"]) == 1
    assert len(data["simplifications"]) == 1
    
    # Cleanup
    await db_service.delete_session(session_id)


def test_get_session_invalid_id():
    """Test GET /api/sessions/{id} with invalid session ID returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/sessions/{fake_id}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_delete_session_valid_id(db_service):
    """Test DELETE /api/sessions/{id} with valid session ID"""
    # Create a test session
    session_id = await db_service.create_session("en")
    
    response = client.delete(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "deleted"
    assert data["session_id"] == session_id
    
    # Verify session is deleted
    session_details = await db_service.get_session_details(session_id)
    assert session_details is None


def test_delete_session_invalid_id():
    """Test DELETE /api/sessions/{id} with invalid session ID returns 404"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/sessions/{fake_id}")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_delete_session_cascade(db_service):
    """Test that deleting a session removes all related data"""
    # Create session with related data
    session_id = await db_service.create_session("en")
    await db_service.add_transcript_chunk(session_id, "Test transcript")
    await db_service.add_simplification(session_id, "term", "explanation")
    await db_service.save_summary(session_id, {
        "title": "Test",
        "diagnosis": "Test diagnosis",
        "medications": [],
        "instructions": [],
        "follow_up": "Test",
        "key_points": []
    })
    
    # Verify data exists
    session_details = await db_service.get_session_details(session_id)
    assert len(session_details["transcript"]) > 0
    assert len(session_details["simplifications"]) > 0
    assert session_details["summary"] is not None
    
    # Delete session
    response = client.delete(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    
    # Verify all data is gone
    deleted_session = await db_service.get_session_details(session_id)
    assert deleted_session is None


def test_http_status_codes():
    """Test that appropriate HTTP status codes are returned"""
    # 200 OK for successful requests
    response = client.get("/health")
    assert response.status_code == 200
    
    # 404 Not Found for non-existent resources
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/sessions/{fake_id}")
    assert response.status_code == 404
    
    # 404 for non-existent routes
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
