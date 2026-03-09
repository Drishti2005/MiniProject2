# Property-based tests for database operations
# Feature: sidekick-medical-assistant

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from uuid import UUID
import asyncio


# Feature: sidekick-medical-assistant, Property 8: Simplification Accumulation Invariant
@given(
    term=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    explanation=st.text(min_size=10, max_size=200).filter(lambda s: s.strip())
)
@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.asyncio
async def test_simplification_accumulation_invariant(db_service, test_session, term, explanation):
    """
    Property 8: Simplification Accumulation Invariant
    For any session, adding a new simplification should increase the list size by exactly 1
    Validates: Requirements 2.6
    """
    # Get initial count
    initial_count = await db_service.get_simplification_count(test_session)
    
    # Add simplification
    await db_service.add_simplification(test_session, term, explanation)
    
    # Get new count
    new_count = await db_service.get_simplification_count(test_session)
    
    # Verify invariant: count increased by exactly 1
    assert new_count == initial_count + 1, \
        f"Expected count to increase by 1, but went from {initial_count} to {new_count}"


# Feature: sidekick-medical-assistant, Property 9: Simplification Persistence Completeness
@given(
    term=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    explanation=st.text(min_size=10, max_size=200).filter(lambda s: s.strip())
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_simplification_persistence_completeness(db_service, test_session, term, explanation):
    """
    Property 9: Simplification Persistence Completeness
    For any simplification generated, a database record should be created containing 
    session_id, term, explanation, and timestamp fields
    Validates: Requirements 2.7
    """
    # Add simplification
    await db_service.add_simplification(test_session, term, explanation)
    
    # Retrieve session details
    session_details = await db_service.get_session_details(test_session)
    
    # Find the simplification we just added
    simplifications = session_details["simplifications"]
    matching = [s for s in simplifications if s["term"] == term and s["explanation"] == explanation]
    
    # Verify at least one matching simplification exists
    assert len(matching) > 0, "Simplification was not persisted to database"
    
    # Verify all required fields are present
    simplification = matching[-1]  # Get the most recent one
    assert "id" in simplification, "Missing id field"
    assert "session_id" in simplification, "Missing session_id field"
    assert "term" in simplification, "Missing term field"
    assert "explanation" in simplification, "Missing explanation field"
    assert "timestamp" in simplification, "Missing timestamp field"
    
    # Verify field values
    assert simplification["session_id"] == test_session
    assert simplification["term"] == term
    assert simplification["explanation"] == explanation


# Feature: sidekick-medical-assistant, Property 35: Session Deletion Cascade
@given(
    transcript_text=st.text(min_size=10, max_size=200).filter(lambda s: s.strip()),
    term=st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
    explanation=st.text(min_size=10, max_size=200).filter(lambda s: s.strip())
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_session_deletion_cascade(db_service, transcript_text, term, explanation):
    """
    Property 35: Session Deletion Cascade
    For any session deletion, all related records in transcript_chunks, simplifications, 
    and summaries tables should be deleted (cascade delete)
    Validates: Requirements 7.9, 12.7
    """
    # Create a new session for this test
    session_id = await db_service.create_session("en")
    
    # Add data to all related tables
    await db_service.add_transcript_chunk(session_id, transcript_text)
    await db_service.add_simplification(session_id, term, explanation)
    await db_service.save_summary(session_id, {
        "title": "Test Summary",
        "diagnosis": "Test diagnosis",
        "medications": ["med1"],
        "instructions": ["instruction1"],
        "follow_up": "Follow up in 1 week",
        "key_points": ["point1"]
    })
    
    # Verify data exists
    session_details = await db_service.get_session_details(session_id)
    assert session_details is not None
    assert len(session_details["transcript"]) > 0
    assert len(session_details["simplifications"]) > 0
    assert session_details["summary"] is not None
    
    # Delete the session
    await db_service.delete_session(session_id)
    
    # Verify session and all related data are gone
    deleted_session = await db_service.get_session_details(session_id)
    assert deleted_session is None, "Session should be deleted but still exists"


# Feature: sidekick-medical-assistant, Property 37: Transcript Chunk Persistence
@given(
    text=st.text(min_size=10, max_size=500).filter(lambda s: s.strip())
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_transcript_chunk_persistence(db_service, test_session, text):
    """
    Property 37: Transcript Chunk Persistence
    For any transcript chunk received by the backend, it should be inserted into 
    the transcript_chunks table with session_id, text, and timestamp
    Validates: Requirements 8.4
    """
    # Add transcript chunk
    await db_service.add_transcript_chunk(test_session, text)
    
    # Retrieve session details
    session_details = await db_service.get_session_details(test_session)
    
    # Find the transcript chunk we just added
    transcript_chunks = session_details["transcript"]
    matching = [t for t in transcript_chunks if t["text"] == text]
    
    # Verify at least one matching chunk exists
    assert len(matching) > 0, "Transcript chunk was not persisted to database"
    
    # Verify all required fields are present
    chunk = matching[-1]  # Get the most recent one
    assert "id" in chunk, "Missing id field"
    assert "session_id" in chunk, "Missing session_id field"
    assert "text" in chunk, "Missing text field"
    assert "timestamp" in chunk, "Missing timestamp field"
    
    # Verify field values
    assert chunk["session_id"] == test_session
    assert chunk["text"] == text


# Feature: sidekick-medical-assistant, Property 38: Session End Timestamp Update
@pytest.mark.asyncio
async def test_session_end_timestamp_update(db_service):
    """
    Property 38: Session End Timestamp Update
    For any session end event, the sessions table should be updated with the ended_at timestamp
    Validates: Requirements 8.7
    """
    # Create a new session
    session_id = await db_service.create_session("en")
    
    # Get initial session details
    initial_details = await db_service.get_session_details(session_id)
    assert initial_details["session"]["ended_at"] is None, "Session should not have ended_at initially"
    
    # End the session
    await db_service.end_session(session_id)
    
    # Get updated session details
    updated_details = await db_service.get_session_details(session_id)
    assert updated_details["session"]["ended_at"] is not None, "Session should have ended_at after ending"
    
    # Cleanup
    await db_service.delete_session(session_id)


# Feature: sidekick-medical-assistant, Property 21: Summary Structure Completeness
@given(
    title=st.text(min_size=5, max_size=100).filter(lambda s: s.strip()),
    diagnosis=st.text(min_size=5, max_size=200).filter(lambda s: s.strip()),
    follow_up=st.text(min_size=5, max_size=200).filter(lambda s: s.strip())
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_summary_structure_completeness(db_service, test_session, title, diagnosis, follow_up):
    """
    Property 21: Summary Structure Completeness
    For any visit summary generated, it should contain all required fields: 
    title, diagnosis, medications (array), instructions (array), follow_up, and key_points (array)
    Validates: Requirements 5.4
    """
    # Create summary with all required fields
    summary_data = {
        "title": title,
        "diagnosis": diagnosis,
        "medications": ["med1", "med2"],
        "instructions": ["instruction1", "instruction2"],
        "follow_up": follow_up,
        "key_points": ["point1", "point2"]
    }
    
    # Save summary
    await db_service.save_summary(test_session, summary_data)
    
    # Retrieve session details
    session_details = await db_service.get_session_details(test_session)
    summary = session_details["summary"]
    
    # Verify summary exists
    assert summary is not None, "Summary should be persisted"
    
    # Verify all required fields are present
    assert "title" in summary, "Missing title field"
    assert "diagnosis" in summary, "Missing diagnosis field"
    assert "medications" in summary, "Missing medications field"
    assert "instructions" in summary, "Missing instructions field"
    assert "follow_up" in summary, "Missing follow_up field"
    assert "key_points" in summary, "Missing key_points field"
    
    # Verify field types
    assert isinstance(summary["medications"], list), "medications should be a list"
    assert isinstance(summary["instructions"], list), "instructions should be a list"
    assert isinstance(summary["key_points"], list), "key_points should be a list"
    
    # Verify field values
    assert summary["title"] == title
    assert summary["diagnosis"] == diagnosis
    assert summary["follow_up"] == follow_up
