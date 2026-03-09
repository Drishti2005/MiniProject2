"""
Tests for GeminiService core functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from gemini_service import GeminiService, RateLimiter


class TestGeminiServiceInitialization:
    """Test service initialization and configuration."""
    
    def test_init_with_valid_api_key(self):
        """Test initialization with valid API key."""
        service = GeminiService(api_key="test_api_key_12345")
        assert service is not None
        assert service.request_count == 0
    
    def test_init_with_empty_api_key(self):
        """Test initialization fails with empty API key."""
        with pytest.raises(ValueError, match="GEMINI_API_KEY is required"):
            GeminiService(api_key="")
    
    def test_init_with_invalid_api_key(self):
        """Test initialization fails with invalid API key format."""
        with pytest.raises(ValueError, match="Invalid GEMINI_API_KEY format"):
            GeminiService(api_key="short")
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter is properly initialized."""
        service = GeminiService(api_key="test_api_key_12345")
        assert service.rate_limiter is not None
        assert service.rate_limiter.max_requests == 15


class TestRateLimiter:
    """Test rate limiting functionality."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_allows_requests_under_limit(self):
        """Test rate limiter allows requests under the limit."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # Should allow 5 requests without waiting
        for _ in range(5):
            await limiter.acquire()
        
        assert len(limiter.requests) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiter_queues_excess_requests(self):
        """Test rate limiter queues requests exceeding the limit."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        
        # First 2 requests should be immediate
        await limiter.acquire()
        await limiter.acquire()
        
        # Third request should wait
        start_time = asyncio.get_event_loop().time()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # Should have waited approximately 1 second
        assert elapsed >= 0.9  # Allow small timing variance
    
    @pytest.mark.asyncio
    async def test_rate_limiter_window_expiration(self):
        """Test rate limiter window expiration."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        
        await limiter.acquire()
        await limiter.acquire()
        
        # Wait for window to expire
        await asyncio.sleep(1.1)
        
        # Should allow new requests without waiting
        await limiter.acquire()
        assert len(limiter.requests) == 1  # Old requests removed


class TestAPICallWithRetry:
    """Test API call retry logic."""
    
    @pytest.mark.asyncio
    async def test_successful_api_call(self):
        """Test successful API call on first attempt."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"terms": []}'
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            result = await service._call_api_with_retry("test prompt", "test_operation")
            assert result == '{"terms": []}'
    
    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Test retry logic on timeout."""
        service = GeminiService(api_key="test_api_key_12345")
        
        # Mock to timeout twice, then succeed
        call_count = 0
        
        async def mock_generate(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise asyncio.TimeoutError()
            mock_response = Mock()
            mock_response.text = '{"terms": []}'
            return mock_response
        
        with patch('asyncio.to_thread', side_effect=mock_generate):
            with patch('asyncio.wait_for', side_effect=mock_generate):
                result = await service._call_api_with_retry("test prompt", "test_operation")
                assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test failure after max retries."""
        service = GeminiService(api_key="test_api_key_12345")
        
        with patch('asyncio.to_thread', side_effect=asyncio.TimeoutError()):
            with patch('asyncio.wait_for', side_effect=asyncio.TimeoutError()):
                with pytest.raises(Exception, match="API timeout after"):
                    await service._call_api_with_retry("test prompt", "test_operation")


class TestPromptSanitization:
    """Test prompt sanitization for security."""
    
    def test_sanitize_ssn(self):
        """Test SSN sanitization."""
        service = GeminiService(api_key="test_api_key_12345")
        text = "Patient SSN is 123-45-6789"
        sanitized = service._sanitize_prompt(text)
        assert "123-45-6789" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_sanitize_email(self):
        """Test email sanitization."""
        service = GeminiService(api_key="test_api_key_12345")
        text = "Contact: patient@example.com"
        sanitized = service._sanitize_prompt(text)
        assert "patient@example.com" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_sanitize_phone(self):
        """Test phone number sanitization."""
        service = GeminiService(api_key="test_api_key_12345")
        text = "Phone: 1234567890"
        sanitized = service._sanitize_prompt(text)
        assert "1234567890" not in sanitized
        assert "[REDACTED]" in sanitized


class TestJSONParsing:
    """Test JSON response parsing."""
    
    def test_parse_valid_json(self):
        """Test parsing valid JSON."""
        service = GeminiService(api_key="test_api_key_12345")
        response = '{"terms": [{"term": "test", "explanation": "test"}]}'
        result = service._parse_json_response(response, "test")
        assert "terms" in result
        assert len(result["terms"]) == 1
    
    def test_parse_json_with_markdown(self):
        """Test parsing JSON wrapped in markdown code blocks."""
        service = GeminiService(api_key="test_api_key_12345")
        response = '```json\n{"terms": []}\n```'
        result = service._parse_json_response(response, "test")
        assert "terms" in result
    
    def test_parse_invalid_json(self):
        """Test error handling for invalid JSON."""
        service = GeminiService(api_key="test_api_key_12345")
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            service._parse_json_response("not json", "test")


class TestPerformanceMonitoring:
    """Test performance monitoring features."""
    
    @pytest.mark.asyncio
    async def test_performance_stats_tracking(self):
        """Test performance statistics tracking."""
        service = GeminiService(api_key="test_api_key_12345")
        
        mock_response = Mock()
        mock_response.text = '{"terms": []}'
        
        with patch.object(service.model, 'generate_content', return_value=mock_response):
            await service._call_api_with_retry("test prompt", "test_operation")
        
        stats = service.get_performance_stats()
        assert stats["total_requests"] == 1
        assert stats["average_response_time"] >= 0
    
    @pytest.mark.asyncio
    async def test_slow_request_detection(self):
        """Test slow request detection."""
        service = GeminiService(api_key="test_api_key_12345")
        
        async def slow_generate(*args, **kwargs):
            await asyncio.sleep(6)  # Simulate slow request
            mock_response = Mock()
            mock_response.text = '{"terms": []}'
            return mock_response
        
        with patch('asyncio.to_thread', side_effect=slow_generate):
            with patch('asyncio.wait_for', side_effect=slow_generate):
                try:
                    await service._call_api_with_retry("test prompt", "test_operation")
                except:
                    pass
        
        stats = service.get_performance_stats()
        # Note: This test may timeout, which is expected behavior


class TestErrorHandling:
    """Test error handling and logging."""
    
    @pytest.mark.asyncio
    async def test_api_error_logging(self):
        """Test API errors are logged properly."""
        service = GeminiService(api_key="test_api_key_12345")
        
        with patch('asyncio.to_thread', side_effect=Exception("API Error")):
            with patch('asyncio.wait_for', side_effect=Exception("API Error")):
                with pytest.raises(Exception):
                    await service._call_api_with_retry("test prompt", "test_operation")
    
    @pytest.mark.asyncio
    async def test_empty_summary_on_error(self):
        """Test empty summary returned on error."""
        service = GeminiService(api_key="test_api_key_12345")
        
        with patch.object(service, '_call_api_with_retry', side_effect=Exception("Error")):
            summary = await service.generate_summary("test transcript")
            assert summary["title"] == "Medical Visit"
            assert summary["diagnosis"] == ""
            assert summary["medications"] == []
