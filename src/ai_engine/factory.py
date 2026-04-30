"""
AI service factory.

- Tries Gemini first (or Groq first if AI_PROVIDER=groq).
- On GeminiRateLimitError / GeminiAuthError during a live call,
  the wrapper transparently retries with Groq.
- All errors written to ai_debug.log.
"""

import logging
import os
from typing import Dict, List

from .base import _write_debug, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


class _FallbackService:
    """
    Wraps a primary provider and falls back to a secondary on
    rate-limit (429) or auth (403) errors from the primary.
    """

    def __init__(self, primary, secondary=None):
        self._primary   = primary
        self._secondary = secondary
        self._using_fallback = False

    def _provider_name(self):
        return type(self._primary).__name__

    async def _with_fallback(self, method: str, *args, **kwargs):
        from .gemini_provider import GeminiRateLimitError, GeminiAuthError
        try:
            result = await getattr(self._primary, method)(*args, **kwargs)
            if self._using_fallback:
                _write_debug("INFO", "Factory", method, "Primary provider recovered")
                self._using_fallback = False
            return result
        except (GeminiRateLimitError, GeminiAuthError) as e:
            _write_debug("WARN", "Factory", method,
                         f"Primary auth/rate error ({type(e).__name__}: {e}), switching to fallback")
            logger.warning(f"[AI Factory] Primary failed ({e}), using fallback for {method}")
            self._using_fallback = True
            if self._secondary:
                return await getattr(self._secondary, method)(*args, **kwargs)
            # No configured secondary — use mock so the app keeps running
            from .mock_provider import MockProvider
            if not hasattr(self, "_mock"):
                self._mock = MockProvider()
            return await getattr(self._mock, method)(*args, **kwargs)
        except Exception as e:
            if self._using_fallback and self._secondary:
                return await getattr(self._secondary, method)(*args, **kwargs)
            raise

    async def get_insights(self, transcript: str) -> Dict:
        return await self._with_fallback("get_insights", transcript)

    async def generate_summary(self, full_transcript: str) -> Dict:
        return await self._with_fallback("generate_summary", full_transcript)

    async def translate_text(self, text: str, target_language: str) -> str:
        return await self._with_fallback("translate_text", text, target_language)

    async def explain_question(self, question: str, context: str = "") -> str:
        return await self._with_fallback("explain_question", question, context)

    # Legacy compat
    async def simplify_terms(self, transcript: str) -> List[Dict[str, str]]:
        result = await self.get_insights(transcript)
        return result.get("medical_terms", [])

    async def suggest_questions(self, full_transcript: str) -> List[str]:
        result = await self.get_insights(full_transcript)
        return result.get("suggested_questions", [])

    @property
    def active_provider(self) -> str:
        if self._using_fallback and self._secondary:
            return type(self._secondary).__name__
        return type(self._primary).__name__


def create_ai_service() -> _FallbackService:
    """
    Build and return the AI service.

    Resolution:
    1. AI_PROVIDER=groq  → Groq primary, Gemini secondary
    2. Otherwise         → Gemini primary, Groq secondary
    3. If primary fails to init, try secondary alone.
    """
    pref       = os.getenv("AI_PROVIDER", "gemini").lower().strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key   = os.getenv("GROQ_API_KEY", "")

    gemini_svc = None
    groq_svc   = None

    # Try to build Gemini
    if gemini_key and not gemini_key.startswith("your_"):
        try:
            from .gemini_provider import GeminiProvider
            gemini_svc = GeminiProvider(gemini_key)
            _write_debug("INFO", "Factory", "init", "GeminiProvider created successfully")
        except Exception as e:
            _write_debug("ERROR", "Factory", "init", f"GeminiProvider failed: {e}")
            logger.warning(f"[AI Factory] Gemini init failed: {e}")

    # Try to build Groq
    if groq_key and not groq_key.startswith("your_"):
        try:
            from .groq_provider import GroqProvider
            groq_svc = GroqProvider(groq_key)
            _write_debug("INFO", "Factory", "init", "GroqProvider created successfully")
        except Exception as e:
            _write_debug("ERROR", "Factory", "init", f"GroqProvider failed: {e}")
            logger.warning(f"[AI Factory] Groq init failed: {e}")

    if pref == "groq":
        primary, secondary = groq_svc, gemini_svc
    else:
        primary, secondary = gemini_svc, groq_svc

    if primary is None and secondary is None:
        # No real provider available — use mock so the app still runs
        _write_debug("WARN", "Factory", "init",
                     "No real API keys configured. Falling back to MockProvider.")
        logger.warning("[AI Factory] No real API keys — using MockProvider (demo mode)")
        from .mock_provider import MockProvider
        return _FallbackService(MockProvider(), None)

    if primary is None:
        logger.warning("[AI Factory] Primary unavailable, using secondary as primary")
        primary, secondary = secondary, None

    svc = _FallbackService(primary, secondary)
    _write_debug("INFO", "Factory", "init",
                 f"Service ready: primary={type(primary).__name__}, "
                 f"secondary={type(secondary).__name__ if secondary else 'None'}")
    logger.info(f"[AI Factory] Ready — primary={type(primary).__name__}, "
                f"secondary={type(secondary).__name__ if secondary else 'None'}")
    return svc
