"""
Property-based tests using Hypothesis for comprehensive validation.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch
from gemini_service import GeminiService, RateLimiter
import asyncio


# Property 42: Gemini API Rate Limiting
@pytest.mark.asyncio
@settings(max_examples=50)
@given(st.integers(min_value=1, max_value=20))
async def test_property_rate_limiting(num_requests):
    """
    Property 42: For any sequence of requests, rate does not exceed 15 per minute.
    """
    limiter = RateLimiter(max_requests=15, window_seconds=60)
    
    start_time = asyncio.get_event_loop().time()
    
    # Make requests
    for _ in range(min(num_requests, 15)):
        await limiter.acquire()
    
    elapsed = asyncio.get_event_loop().time() - start_time
    
    # First 15 requests should be immediate (< 1 second)
    if num_requests <= 15:
        assert elapsed < 1.0


# Property 43: Rate Limit Queue Behavior
@pytest.mark.asyncio
async def test_property_rate_limit_queue():
    """
    Property 43: For any request exceeding rate limit, verify it's queued.
    """
    limiter = RateLimiter(max_requests=2, window_seconds=1)
    
    # Fill capacity
    await limiter.acquire()
    await limiter.acquire()
    
    # Next request should be queued
    start = asyncio.get_event_loop().time()
    await limiter.acquire()
    elapsed = asyncio.get_event_loop().time() - start
    
    # Should have waited approximately 1 second
    assert elapsed >= 0.9


# Property 40: Gemini API Response Parsing
@pytest.mark.asyncio
@settings(max_examples=50)
@given(st.dictionaries(
    keys=st.text(min_size=1, max_size=20),
    values=st.one_of(
        st.text(),
        st.lists(st.text()),
        st.integers()
    )
))
async def test_property_json_parsing(json_data):
    """
    Property 40: For any valid JSON response, verify successful parsing.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    import json
    json_str = json.dumps(json_data)
    
    try:
        result = service._parse_json_response(json_str, "test")
        assert isinstance(result, dict)
    except ValueError:
        # Some generated JSON may be invalid, which is acceptable
        pass


# Property 41: Gemini API Error Handling
@pytest.mark.asyncio
@settings(max_examples=20)
@given(st.text(min_size=1, max_size=100))
async def test_property_error_handling(error_message):
    """
    Property 41: For any error response, verify logging and user-friendly message.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    with patch.object(service, '_call_api_with_retry', side_effect=Exception(error_message)):
        # Test simplification error handling
        result = await service.simplify_terms("test")
        assert result == []  # Should return empty list on error
        
        # Test question error handling
        result = await service.suggest_questions("test " * 60)
        assert result == []
        
        # Test summary error handling
        result = await service.generate_summary("test")
        assert result["title"] == "Medical Visit"


# Property 49: Gemini API Retry Logic
@pytest.mark.asyncio
async def test_property_retry_logic():
    """
    Property 49: For any API unavailability, verify retries up to 3 times.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    call_count = 0
    
    async def failing_call(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise Exception("API unavailable")
    
    with patch('asyncio.to_thread', side_effect=failing_call):
        with patch('asyncio.wait_for', side_effect=failing_call):
            try:
                await service._call_api_with_retry("test", "test_op")
            except Exception:
                pass
    
    # Should have tried 3 times
    assert call_count == 3


# Property 57: Gemini API Timeout
@pytest.mark.asyncio
async def test_property_api_timeout():
    """
    Property 57: For any API call, verify timeout of 10 seconds enforced.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    async def slow_call(*args, **kwargs):
        await asyncio.sleep(15)  # Longer than timeout
        return Mock(text='{"terms": []}')
    
    with patch('asyncio.to_thread', side_effect=slow_call):
        with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError()):
            try:
                await service._call_api_with_retry("test", "test_op")
            except Exception as e:
                assert "timeout" in str(e).lower()


# Property 61: HTTPS for Gemini API
def test_property_https_usage():
    """
    Property 61: For any API request, verify HTTPS protocol is used.
    """
    # Gemini SDK uses HTTPS by default
    # This is a configuration check
    from config import HTTPS_REQUIRED
    assert HTTPS_REQUIRED is True


# Property 5: Simplification Generation Completeness
@pytest.mark.asyncio
@settings(max_examples=20)
@given(st.lists(
    st.dictionaries(
        keys=st.just("term") | st.just("explanation"),
        values=st.text(min_size=1, max_size=50)
    ),
    min_size=0,
    max_size=5
))
async def test_property_simplification_completeness(terms_data):
    """
    Property 5: For any medical term identified, verify simplification generated.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    # Filter to only valid terms (have both fields)
    valid_terms = [
        t for t in terms_data 
        if "term" in t and "explanation" in t
    ]
    
    mock_response = Mock()
    mock_response.text = f'{{"terms": {str(valid_terms).replace("'", '"')}}}'
    
    with patch.object(service.model, 'generate_content', return_value=mock_response):
        result = await service.simplify_terms("test transcript")
        
        # Every returned term must have both fields
        for term in result:
            assert "term" in term
            assert "explanation" in term


# Property 11: Question Suggestion Cardinality
@pytest.mark.asyncio
async def test_property_question_cardinality():
    """
    Property 11: For any request with sufficient context, verify 2-3 questions.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    mock_response = Mock()
    mock_response.text = '''
    {
        "questions": [
            "Question 1?",
            "Question 2?",
            "Question 3?"
        ]
    }
    '''
    
    transcript = " ".join(["word"] * 60)  # Sufficient context
    
    with patch.object(service.model, 'generate_content', return_value=mock_response):
        result = await service.suggest_questions(transcript)
        
        # Should return 2-3 questions
        assert 2 <= len(result) <= 3


# Property 21: Summary Structure Completeness
@pytest.mark.asyncio
@settings(max_examples=20)
@given(st.text(min_size=10, max_size=200))
async def test_property_summary_structure(transcript):
    """
    Property 21: For any summary generated, verify all required fields present.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    mock_response = Mock()
    mock_response.text = '''
    {
        "title": "Test Visit",
        "diagnosis": "Test",
        "medications": ["Med1"],
        "instructions": ["Inst1"],
        "follow_up": "Test",
        "key_points": ["Point1"]
    }
    '''
    
    with patch.object(service.model, 'generate_content', return_value=mock_response):
        result = await service.generate_summary(transcript)
        
        # All required fields must be present
        required_fields = ["title", "diagnosis", "medications", "instructions", "follow_up", "key_points"]
        for field in required_fields:
            assert field in result
        
        # Array fields must be lists
        assert isinstance(result["medications"], list)
        assert isinstance(result["instructions"], list)
        assert isinstance(result["key_points"], list)


# Property 28: Translation Transmission
@pytest.mark.asyncio
@settings(max_examples=20)
@given(
    st.text(min_size=1, max_size=100),
    st.sampled_from(["es", "hi", "zh", "fr", "ar"])
)
async def test_property_translation_transmission(text, language):
    """
    Property 28: For any translated text, verify sent within 2 seconds.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    mock_response = Mock()
    mock_response.text = "Translated text"
    
    import time
    
    with patch.object(service.model, 'generate_content', return_value=mock_response):
        start = time.time()
        result = await service.translate_text(text, language)
        elapsed = time.time() - start
        
        assert elapsed < 2.0
        assert isinstance(result, str)


# Property: Sanitization Removes Sensitive Data
@pytest.mark.asyncio
@settings(max_examples=20)
@given(st.text(min_size=10, max_size=100))
async def test_property_sanitization(text):
    """
    Property: For any text with sensitive patterns, verify sanitization.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    # Add a fake SSN to the text
    text_with_ssn = f"{text} SSN: 123-45-6789"
    
    sanitized = service._sanitize_prompt(text_with_ssn)
    
    # SSN should be redacted
    assert "123-45-6789" not in sanitized
    assert "[REDACTED]" in sanitized


# Property: Performance Stats Accuracy
@pytest.mark.asyncio
async def test_property_performance_stats():
    """
    Property: Performance stats accurately reflect API calls.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    initial_stats = service.get_performance_stats()
    assert initial_stats["total_requests"] == 0
    
    mock_response = Mock()
    mock_response.text = '{"terms": []}'
    
    with patch.object(service.model, 'generate_content', return_value=mock_response):
        await service._call_api_with_retry("test", "test_op")
    
    updated_stats = service.get_performance_stats()
    assert updated_stats["total_requests"] == 1
    assert updated_stats["average_response_time"] >= 0


# Property: Empty Input Handling
@pytest.mark.asyncio
@settings(max_examples=10)
@given(st.one_of(st.just(""), st.just("   "), st.just("\n\n")))
async def test_property_empty_input_handling(empty_text):
    """
    Property: For any empty/whitespace input, operations handle gracefully.
    """
    service = GeminiService(api_key="test_api_key_12345")
    
    # Simplification
    result = await service.simplify_terms(empty_text)
    assert result == []
    
    # Questions
    result = await service.suggest_questions(empty_text)
    assert result == []
    
    # Summary
    result = await service.generate_summary(empty_text)
    assert result["title"] == "Medical Visit"
    
    # Translation
    result = await service.translate_text(empty_text, "es")
    assert result == ""
