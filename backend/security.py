# TEAM: Backend Infrastructure
# Security utilities for data sanitization and input validation
# Ensures no sensitive data is logged and all inputs are validated

import re
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Patterns for sensitive medical information
SENSITIVE_PATTERNS = [
    # Patient identifiers
    (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # Social Security Number
    (r'\b\d{10}\b', '[PHONE]'),  # Phone number
    (r'\b[A-Z]{2}\d{6,8}\b', '[ID]'),  # Medical ID
    
    # Personal information
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
    (r'\b\d{1,5}\s+\w+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b', '[ADDRESS]'),  # Address
    
    # Medical record numbers
    (r'\bMRN[:\s]*\d+\b', '[MRN]'),
    (r'\bPatient\s+ID[:\s]*\d+\b', '[PATIENT_ID]'),
    
    # Dates of birth
    (r'\b(0?[1-9]|1[0-2])/(0?[1-9]|[12][0-9]|3[01])/\d{4}\b', '[DOB]'),
    (r'\b\d{4}-(0?[1-9]|1[0-2])-(0?[1-9]|[12][0-9]|3[01])\b', '[DOB]'),
]


def sanitize_log_message(message: str) -> str:
    """
    Sanitize log messages to remove sensitive medical information
    
    Args:
        message: Original log message
    
    Returns:
        Sanitized message with sensitive data replaced
    
    Requirements: 14.5
    """
    sanitized = message
    
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format (UUID)
    
    Args:
        session_id: Session ID to validate
    
    Returns:
        True if valid, False otherwise
    
    Requirements: 14.4
    """
    # UUID format: 8-4-4-4-12 hexadecimal characters
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, session_id, re.IGNORECASE))


def validate_language_code(language: str) -> bool:
    """
    Validate language code (ISO 639-1).
    Accepts any 2-3 character code to avoid blocking valid languages.
    """
    if not language or not isinstance(language, str):
        return False
    # Accept any 2-3 letter ISO code rather than a hardcoded allowlist
    return bool(re.match(r'^[a-z]{2,3}$', language.lower()))


def validate_text_input(text: str, max_length: int = 10000) -> tuple[bool, str]:
    """
    Validate text input for transcript and other text fields
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Requirements: 14.4
    """
    if not text:
        return False, "Text cannot be empty"
    
    if not isinstance(text, str):
        return False, "Text must be a string"
    
    if len(text) > max_length:
        return False, f"Text exceeds maximum length of {max_length} characters"
    
    # Check for null bytes (security risk)
    if '\x00' in text:
        return False, "Text contains invalid null bytes"
    
    return True, ""


def sanitize_text_input(text: str) -> str:
    """
    Sanitize text input by removing potentially dangerous characters
    
    Args:
        text: Text to sanitize
    
    Returns:
        Sanitized text
    
    Requirements: 14.4
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    # Trim whitespace
    text = text.strip()
    
    return text


def ensure_no_audio_storage(session_id: str, storage_path: str = ".") -> bool:
    """
    Verify that no audio files are stored for a session
    
    Args:
        session_id: Session ID to check
        storage_path: Path to check for audio files
    
    Returns:
        True if no audio files found, False otherwise
    
    Requirements: 14.1
    """
    import os
    
    # Audio file extensions to check
    audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma']
    
    # Check if any audio files exist with the session ID in the name
    for root, dirs, files in os.walk(storage_path):
        for file in files:
            if session_id in file and any(file.lower().endswith(ext) for ext in audio_extensions):
                logger.warning(f"⚠️  Audio file found for session {session_id}: {file}")
                return False
    
    return True


class SanitizingLogger:
    """Logger wrapper that automatically sanitizes sensitive data"""
    
    def __init__(self, logger_name: str):
        self.logger = logging.getLogger(logger_name)
    
    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization"""
        sanitized = sanitize_log_message(message)
        self.logger.info(sanitized, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization"""
        sanitized = sanitize_log_message(message)
        self.logger.warning(sanitized, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization"""
        sanitized = sanitize_log_message(message)
        self.logger.error(sanitized, *args, **kwargs)
    
    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitization"""
        sanitized = sanitize_log_message(message)
        self.logger.debug(sanitized, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization"""
        sanitized = sanitize_log_message(message)
        self.logger.critical(sanitized, *args, **kwargs)


def validate_websocket_message(message: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate WebSocket message structure
    
    Args:
        message: Message dictionary to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    
    Requirements: 11.5
    """
    if not isinstance(message, dict):
        return False, "Message must be a dictionary"
    
    if "type" not in message:
        return False, "Message must have a 'type' field"
    
    message_type = message.get("type")
    valid_types = ["transcript", "end_session", "language_change", "ping", "question_ask", "doctor_reply"]
    
    if message_type not in valid_types:
        return False, f"Invalid message type: {message_type}"
    
    # Validate transcript message
    if message_type == "transcript":
        if "text" not in message:
            return False, "Transcript message must have 'text' field"
        
        if "language" not in message:
            return False, "Transcript message must have 'language' field"
        
        is_valid, error = validate_text_input(message["text"])
        if not is_valid:
            return False, f"Invalid text: {error}"
        
        if not validate_language_code(message["language"]):
            return False, f"Invalid language code: {message['language']}"
    
    return True, ""
