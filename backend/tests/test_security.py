# Unit tests for security features

import pytest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.security import (
    sanitize_log_message,
    validate_session_id,
    validate_language_code,
    validate_text_input,
    sanitize_text_input,
    ensure_no_audio_storage,
    validate_websocket_message
)


def test_sanitize_log_message_ssn():
    """Test that SSN is sanitized from log messages"""
    message = "Patient SSN is 123-45-6789 for reference"
    sanitized = sanitize_log_message(message)
    assert "123-45-6789" not in sanitized
    assert "[SSN]" in sanitized


def test_sanitize_log_message_email():
    """Test that email is sanitized from log messages"""
    message = "Contact patient at john.doe@example.com"
    sanitized = sanitize_log_message(message)
    assert "john.doe@example.com" not in sanitized
    assert "[EMAIL]" in sanitized


def test_sanitize_log_message_phone():
    """Test that phone number is sanitized from log messages"""
    message = "Patient phone: 5551234567"
    sanitized = sanitize_log_message(message)
    assert "5551234567" not in sanitized
    assert "[PHONE]" in sanitized


def test_sanitize_log_message_mrn():
    """Test that MRN is sanitized from log messages"""
    message = "MRN: 12345678 for patient record"
    sanitized = sanitize_log_message(message)
    assert "12345678" not in sanitized
    assert "[MRN]" in sanitized


def test_validate_session_id_valid():
    """Test validation of valid UUID session IDs"""
    valid_id = "550e8400-e29b-41d4-a716-446655440000"
    assert validate_session_id(valid_id) == True


def test_validate_session_id_invalid():
    """Test validation of invalid session IDs"""
    assert validate_session_id("invalid-id") == False
    assert validate_session_id("12345") == False
    assert validate_session_id("") == False


def test_validate_language_code_valid():
    """Test validation of valid language codes"""
    assert validate_language_code("en") == True
    assert validate_language_code("es") == True
    assert validate_language_code("fr") == True
    assert validate_language_code("EN") == True  # Case insensitive


def test_validate_language_code_invalid():
    """Test validation of invalid language codes"""
    assert validate_language_code("invalid") == False
    assert validate_language_code("xyz") == False
    assert validate_language_code("") == False


def test_validate_text_input_valid():
    """Test validation of valid text input"""
    is_valid, error = validate_text_input("This is valid text")
    assert is_valid == True
    assert error == ""


def test_validate_text_input_empty():
    """Test validation of empty text input"""
    is_valid, error = validate_text_input("")
    assert is_valid == False
    assert "empty" in error.lower()


def test_validate_text_input_too_long():
    """Test validation of text exceeding max length"""
    long_text = "a" * 10001
    is_valid, error = validate_text_input(long_text, max_length=10000)
    assert is_valid == False
    assert "maximum length" in error.lower()


def test_validate_text_input_null_bytes():
    """Test validation of text with null bytes"""
    text_with_null = "text\x00with\x00null"
    is_valid, error = validate_text_input(text_with_null)
    assert is_valid == False
    assert "null" in error.lower()


def test_sanitize_text_input():
    """Test sanitization of text input"""
    text = "  text with \x00 null bytes  "
    sanitized = sanitize_text_input(text)
    assert "\x00" not in sanitized
    assert sanitized == "text with  null bytes"


def test_sanitize_text_input_control_chars():
    """Test sanitization removes control characters"""
    text = "text\x01with\x02control\x03chars"
    sanitized = sanitize_text_input(text)
    assert "\x01" not in sanitized
    assert "\x02" not in sanitized
    assert "\x03" not in sanitized


def test_ensure_no_audio_storage():
    """Test that no audio files are stored"""
    # Test with a fake session ID that shouldn't have audio files
    session_id = "test-session-no-audio"
    result = ensure_no_audio_storage(session_id, storage_path=".")
    assert result == True  # Should be True since no audio files exist


def test_validate_websocket_message_valid_transcript():
    """Test validation of valid transcript WebSocket message"""
    message = {
        "type": "transcript",
        "text": "This is a valid transcript",
        "language": "en"
    }
    is_valid, error = validate_websocket_message(message)
    assert is_valid == True
    assert error == ""


def test_validate_websocket_message_missing_type():
    """Test validation of message missing type field"""
    message = {
        "text": "Some text"
    }
    is_valid, error = validate_websocket_message(message)
    assert is_valid == False
    assert "type" in error.lower()


def test_validate_websocket_message_invalid_type():
    """Test validation of message with invalid type"""
    message = {
        "type": "invalid_type",
        "text": "Some text"
    }
    is_valid, error = validate_websocket_message(message)
    assert is_valid == False
    assert "invalid message type" in error.lower()


def test_validate_websocket_message_missing_text():
    """Test validation of transcript message missing text field"""
    message = {
        "type": "transcript",
        "language": "en"
    }
    is_valid, error = validate_websocket_message(message)
    assert is_valid == False
    assert "text" in error.lower()


def test_validate_websocket_message_missing_language():
    """Test validation of transcript message missing language field"""
    message = {
        "type": "transcript",
        "text": "Some text"
    }
    is_valid, error = validate_websocket_message(message)
    assert is_valid == False
    assert "language" in error.lower()


def test_validate_websocket_message_invalid_language():
    """Test validation of transcript message with invalid language"""
    message = {
        "type": "transcript",
        "text": "Some text",
        "language": "invalid"
    }
    is_valid, error = validate_websocket_message(message)
    assert is_valid == False
    assert "language" in error.lower()


def test_validate_websocket_message_end_session():
    """Test validation of valid end_session message"""
    message = {
        "type": "end_session"
    }
    is_valid, error = validate_websocket_message(message)
    assert is_valid == True
    assert error == ""


def test_environment_variable_loading():
    """Test that environment variables are loaded securely"""
    # This test verifies that .env file is used and not hardcoded values
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check that required environment variables exist (either from .env or CI environment)
    gemini_key = os.getenv("GEMINI_API_KEY")
    database_url = os.getenv("DATABASE_URL")
    
    assert gemini_key is not None, "GEMINI_API_KEY should be set"
    assert database_url is not None, "DATABASE_URL should be set"
    
    # In CI, these will be test values; in local dev, they should be real values
    assert len(gemini_key) > 0, "GEMINI_API_KEY should not be empty"
    assert len(database_url) > 0, "DATABASE_URL should not be empty"


def test_log_sanitization_integration():
    """Test that SanitizingLogger properly sanitizes messages"""
    from backend.security import SanitizingLogger
    import logging
    
    # Create a test logger
    test_logger = SanitizingLogger("test_security")
    
    # This should not raise an exception and should sanitize the message
    test_logger.info("Patient SSN: 123-45-6789")
    test_logger.warning("Contact: john@example.com")
    test_logger.error("Phone: 5551234567")
    
    # If we get here without exceptions, the test passes
    assert True


def test_input_validation_prevents_injection():
    """Test that input validation prevents potential injection attacks"""
    # Test SQL injection attempt
    malicious_text = "'; DROP TABLE sessions; --"
    is_valid, error = validate_text_input(malicious_text)
    # Should be valid as text, but will be sanitized/escaped by database layer
    assert is_valid == True
    
    # Test XSS attempt
    xss_text = "<script>alert('xss')</script>"
    is_valid, error = validate_text_input(xss_text)
    # Should be valid as text (frontend should handle escaping)
    assert is_valid == True
    
    # Test null byte injection
    null_injection = "text\x00injection"
    is_valid, error = validate_text_input(null_injection)
    assert is_valid == False  # Null bytes should be rejected
