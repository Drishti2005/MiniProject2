"""
AI Engine — Gemini + Groq with automatic fallback.
All errors logged to src/ai_engine/ai_debug.log.
"""

from .factory import create_ai_service

__all__ = ["create_ai_service"]
