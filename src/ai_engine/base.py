"""
Base class and shared utilities for all AI providers.
All API errors are written to ai_debug.log in addition to the normal logger.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List

# ── Debug log file (append-only, human-readable) ──────────────
_DEBUG_LOG = os.path.join(os.path.dirname(__file__), "ai_debug.log")


def _write_debug(level: str, provider: str, operation: str, message: str):
    """Append a line to ai_debug.log."""
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] [{level}] [{provider}] [{operation}] {message}\n")
    except Exception:
        pass  # never crash the app over logging


logger = logging.getLogger(__name__)

# ── Supported translation languages ───────────────────────────
SUPPORTED_LANGUAGES = {
    "es": "Spanish",
    "hi": "Hindi",
    "zh": "Mandarin Chinese",
    "fr": "French",
    "ar": "Arabic",
    "de": "German",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
}

SENSITIVE_PATTERNS = [
    r'\b\d{3}-\d{2}-\d{4}\b',
    r'\b\d{10,}\b',
    r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
    r'\bMRN[:\s]*\d+\b',
]


class BaseAIService:
    """Shared helpers used by every provider."""

    _provider_name = "BaseAI"

    def _sanitize(self, text: str) -> str:
        for p in SENSITIVE_PATTERNS:
            text = re.sub(p, "[REDACTED]", text, flags=re.IGNORECASE)
        return text

    def _parse_json(self, raw: str, operation: str) -> Dict:
        """Extract JSON from raw API response (handles markdown fences)."""
        cleaned = raw.strip()
        if "```json" in cleaned:
            start = cleaned.find("```json") + 7
            end = cleaned.find("```", start)
            cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.find("```") + 3
            end = cleaned.find("```", start)
            cleaned = cleaned[start:end].strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            msg = f"JSON parse error: {e} | raw[:300]={raw[:300]}"
            logger.error(f"[{operation}] {msg}")
            _write_debug("ERROR", self._provider_name, operation, msg)
            raise ValueError(msg)

    def _log_api_error(self, operation: str, error: Exception, attempt: int = 0):
        msg = f"attempt={attempt} error={type(error).__name__}: {error}"
        logger.error(f"[{self._provider_name}][{operation}] {msg}")
        _write_debug("ERROR", self._provider_name, operation, msg)

    def _log_api_success(self, operation: str, elapsed: float):
        msg = f"completed in {elapsed:.2f}s"
        logger.info(f"[{self._provider_name}][{operation}] {msg}")
        _write_debug("INFO", self._provider_name, operation, msg)

    def _empty_summary(self) -> Dict:
        return {
            "title": "Medical Visit",
            "diagnosis": "",
            "medications": [],
            "instructions": [],
            "follow_up": "",
            "key_points": [],
        }
