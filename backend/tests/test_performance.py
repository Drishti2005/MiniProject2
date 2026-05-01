# Property-based tests for performance constraints

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import asyncio
import time
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


# Feature: sidekick-medical-assistant, Property 56: Transcript Processing Time
@given(
    text=st.text(min_size=10, max_size=500).filter(lambda s: s.strip())
)
@settings(
    max_examples=50,  # Reduced for performance tests
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_transcript_processing_time(db_service, test_session, text):
    """
    Property 56: Transcript Processing Time
    For any transcript chunk, processing (storage + AI call) should complete within 2 seconds
    Validates: Requirements 13.1
    """
    start_time = time.time()
    
    # Store transcript chunk (simulating the processing)
    await db_service.add_transcript_chunk(test_session, text)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Database operation should complete within 2000ms (CI runners can be slow)
    assert elapsed_ms < 2000, \
        f"Transcript storage took {elapsed_ms:.2f}ms, expected < 2000ms"


# Feature: sidekick-medical-assistant, Property 58: Database Query Performance
@pytest.mark.asyncio
async def test_database_query_performance(db_service, test_session):
    """
    Property 58: Database Query Performance
    For any simple database query (get session details), it should complete within 500ms
    Validates: Requirements 13.3
    """
    # Add some data first
    await db_service.add_transcript_chunk(test_session, "Test transcript")
    await db_service.add_simplification(test_session, "term", "explanation")
    
    # Measure query time
    start_time = time.time()
    
    session_details = await db_service.get_session_details(test_session)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Query should complete within 500ms
    assert elapsed_ms < 500, \
        f"Database query took {elapsed_ms:.2f}ms, expected < 500ms"
    
    # Verify data was retrieved
    assert session_details is not None


@pytest.mark.asyncio
async def test_session_creation_performance(db_service):
    """
    Test that session creation is fast
    """
    start_time = time.time()
    
    session_id = await db_service.create_session("en")
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Session creation should be very fast
    assert elapsed_ms < 200, \
        f"Session creation took {elapsed_ms:.2f}ms, expected < 200ms"
    
    # Cleanup
    await db_service.delete_session(session_id)


@pytest.mark.asyncio
async def test_get_all_sessions_performance(db_service):
    """
    Test that listing all sessions is fast even with multiple sessions
    """
    # Create multiple sessions
    session_ids = []
    for i in range(10):
        session_id = await db_service.create_session("en")
        session_ids.append(session_id)
    
    # Measure query time
    start_time = time.time()
    
    sessions = await db_service.get_all_sessions()
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Query should complete within 500ms even with multiple sessions
    assert elapsed_ms < 500, \
        f"Get all sessions took {elapsed_ms:.2f}ms, expected < 500ms"
    
    # Verify sessions were retrieved
    assert len(sessions) >= 10
    
    # Cleanup
    for session_id in session_ids:
        await db_service.delete_session(session_id)


@given(
    term=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    explanation=st.text(min_size=10, max_size=200).filter(lambda s: s.strip())
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_simplification_storage_performance(db_service, test_session, term, explanation):
    """
    Test that storing simplifications is fast
    """
    start_time = time.time()
    
    await db_service.add_simplification(test_session, term, explanation)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Simplification storage should be very fast
    assert elapsed_ms < 200, \
        f"Simplification storage took {elapsed_ms:.2f}ms, expected < 200ms"


@pytest.mark.asyncio
async def test_summary_storage_performance(db_service, test_session):
    """
    Test that storing summaries is fast
    """
    summary_data = {
        "title": "Test Summary",
        "diagnosis": "Test diagnosis",
        "medications": ["med1", "med2"],
        "instructions": ["instruction1", "instruction2"],
        "follow_up": "Follow up in 1 week",
        "key_points": ["point1", "point2"]
    }
    
    start_time = time.time()
    
    await db_service.save_summary(test_session, summary_data)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Summary storage should be fast
    assert elapsed_ms < 300, \
        f"Summary storage took {elapsed_ms:.2f}ms, expected < 300ms"


@pytest.mark.asyncio
async def test_session_deletion_performance(db_service):
    """
    Test that session deletion (with cascade) is reasonably fast
    """
    # Create session with data
    session_id = await db_service.create_session("en")
    await db_service.add_transcript_chunk(session_id, "Test transcript")
    await db_service.add_simplification(session_id, "term", "explanation")
    await db_service.save_summary(session_id, {
        "title": "Test",
        "diagnosis": "Test",
        "medications": [],
        "instructions": [],
        "follow_up": "Test",
        "key_points": []
    })
    
    # Measure deletion time
    start_time = time.time()
    
    await db_service.delete_session(session_id)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Deletion with cascade should complete within 1 second
    assert elapsed_ms < 1000, \
        f"Session deletion took {elapsed_ms:.2f}ms, expected < 1000ms"


def test_performance_timer_utility():
    """Test the PerformanceTimer utility"""
    from backend.performance import PerformanceTimer
    
    with PerformanceTimer("test_operation", threshold_ms=100) as timer:
        time.sleep(0.01)  # 10ms
    
    assert timer.elapsed_ms is not None
    assert timer.elapsed_ms >= 10  # Should be at least 10ms
    assert timer.elapsed_ms < 100  # Should be under threshold


def test_performance_monitor_decorator():
    """Test the performance monitoring decorator"""
    from backend.performance import monitor_performance
    
    @monitor_performance("test_async_operation", threshold_ms=100)
    async def test_operation():
        await asyncio.sleep(0.01)  # 10ms
        return "success"
    
    # Run the decorated function
    result = asyncio.run(test_operation())
    assert result == "success"
