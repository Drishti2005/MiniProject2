"""
Configuration and constants for Gemini AI service.
"""

import os

# Gemini API Configuration
GEMINI_MODEL = "models/gemini-2.5-flash"  # Stable, fast model with good performance
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = 15
RATE_LIMIT_WINDOW_SECONDS = 60

# Timeout Configuration
API_TIMEOUT_SECONDS = 10
REQUEST_TIMEOUT_SECONDS = 2  # For simplification/question/translation responses

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = [1, 2, 4]  # Exponential backoff

# Performance Monitoring
SLOW_REQUEST_THRESHOLD_SECONDS = 5

# Supported Languages for Translation
SUPPORTED_LANGUAGES = {
    "es": "Spanish",
    "hi": "Hindi",
    "zh": "Mandarin",
    "fr": "French",
    "ar": "Arabic"
}

# Model Parameters
TEMPERATURE = 0.3  # Low temperature for consistent medical terminology
MAX_TOKENS = 1024

# JSON Mode Configuration
JSON_MODE_ENABLED = True

# Security
HTTPS_REQUIRED = True
SENSITIVE_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b\d{10,}\b',  # Phone numbers
    r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Email
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_API_CALLS = True
LOG_SLOW_REQUESTS = True
LOG_ERRORS = True

# Cache Configuration (for future optimization)
CACHE_ENABLED = False
CACHE_TTL_SECONDS = 3600
