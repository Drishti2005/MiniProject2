"""
Google Gemini AI provider — uses google-genai SDK.
Logs all errors to ai_debug.log.
Raises GeminiRateLimitError / GeminiAuthError so the factory
can decide whether to fall back to Groq.
"""

import asyncio
import logging
import time
from collections import deque
from typing import Dict, List

from google import genai
from google.genai import types

from .base import BaseAIService, SUPPORTED_LANGUAGES, _write_debug
from .prompts import COMBINED_INSIGHT_PROMPT, VISIT_SUMMARY_PROMPT, TRANSLATION_PROMPT, QUESTION_EXPLANATION_PROMPT

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.0-flash"
API_TIMEOUT    = 45
MAX_RETRIES    = 3
BACKOFF        = [2, 5]
TEMPERATURE    = 0.3
MAX_TOKENS     = 1024
MAX_RPM        = 15
RATE_WINDOW    = 60


class GeminiRateLimitError(Exception):
    """Raised on 429 — caller should fall back to Groq."""


class GeminiAuthError(Exception):
    """Raised on 403 — API key invalid or quota exhausted."""


class _RateLimiter:
    def __init__(self, max_req: int, window: int):
        self.max_req = max_req
        self.window  = window
        self.reqs: deque = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            while self.reqs and self.reqs[0] < now - self.window:
                self.reqs.popleft()
            if len(self.reqs) >= self.max_req:
                wait = self.reqs[0] + self.window - now
                if wait > 0:
                    await asyncio.sleep(wait)
                    return await self.acquire()
            self.reqs.append(now)


class GeminiProvider(BaseAIService):
    """Gemini-backed AI service."""

    _provider_name = "Gemini"

    def __init__(self, api_key: str):
        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid or missing GEMINI_API_KEY")
        self._client = genai.Client(api_key=api_key)
        self._rl     = _RateLimiter(MAX_RPM, RATE_WINDOW)
        self._config = types.GenerateContentConfig(
            temperature=TEMPERATURE,
            max_output_tokens=MAX_TOKENS,
        )
        logger.info(f"GeminiProvider ready (model={GEMINI_MODEL})")
        _write_debug("INFO", "Gemini", "init", f"GeminiProvider initialised with model={GEMINI_MODEL}")

    async def _call(self, prompt: str, op: str) -> str:
        t0 = time.time()
        last_err = None
        for attempt in range(MAX_RETRIES):
            try:
                await self._rl.acquire()
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self._client.models.generate_content,
                        model=GEMINI_MODEL,
                        contents=self._sanitize(prompt),
                        config=self._config,
                    ),
                    timeout=API_TIMEOUT,
                )
                self._log_api_success(op, time.time() - t0)
                return response.text
            except asyncio.TimeoutError as e:
                last_err = e
                self._log_api_error(op, e, attempt)
            except Exception as e:
                last_err = e
                err_str = str(e).lower()
                self._log_api_error(op, e, attempt)
                # 429 rate limit — wait the suggested retry delay then retry
                if "429" in err_str or "resource_exhausted" in err_str:
                    # Check if it's a daily quota exhaustion (limit: 0) vs per-minute
                    if "'limit': 0" in str(e) or "limit: 0" in err_str:
                        # Daily quota gone — fall back permanently
                        _write_debug("WARN", "Gemini", op, "Daily quota exhausted (limit=0). Falling back.")
                        raise GeminiRateLimitError(str(e)) from e
                    import re as _re
                    delay_match = _re.search(r'retrydelay.*?(\d+)s', err_str)
                    wait = min(int(delay_match.group(1)) + 2, 35) if delay_match else 20
                    _write_debug("WARN", "Gemini", op, f"Rate limited. Waiting {wait}s before retry.")
                    if attempt < MAX_RETRIES - 1:
                        await asyncio.sleep(wait)
                        continue
                    raise GeminiRateLimitError(str(e)) from e
                # 403 / invalid key / expired — permanent failure, fall back
                if ("403" in err_str or "400" in err_str or
                        "permission" in err_str or "api_key" in err_str or
                        "invalid" in err_str or "expired" in err_str or
                        "api_key_invalid" in err_str or "not_found" in err_str or
                        "404" in err_str):
                    raise GeminiAuthError(str(e)) from e
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(BACKOFF[attempt])
        raise RuntimeError(f"Gemini failed after {MAX_RETRIES} attempts for {op}: {last_err}")

    # ── Public interface ──────────────────────────────────────

    async def get_insights(self, transcript: str) -> Dict:
        """
        Single combined call → returns dict with keys:
          medical_terms, suggested_questions, session_summary
        """
        if not transcript or not transcript.strip():
            return {"medical_terms": [], "suggested_questions": [], "session_summary": {"key_points": []}}
        try:
            raw  = await self._call(COMBINED_INSIGHT_PROMPT.format(transcript=transcript), "get_insights")
            data = self._parse_json(raw, "get_insights")
            return {
                "medical_terms":       [
                    {
                        "term":        t["term"],
                        "explanation": t["explanation"],
                        "importance":  t.get("importance", "medium"),
                    }
                    for t in data.get("medical_terms", [])
                    if isinstance(t, dict) and "term" in t and "explanation" in t
                ],
                "suggested_questions": data.get("suggested_questions", []),
                "session_summary":     data.get("session_summary", {"key_points": []}),
            }
        except (GeminiRateLimitError, GeminiAuthError):
            raise
        except Exception as e:
            self._log_api_error("get_insights", e)
            return {"medical_terms": [], "suggested_questions": [], "session_summary": {"key_points": []}}

    async def generate_summary(self, full_transcript: str) -> Dict:
        if not full_transcript or not full_transcript.strip():
            return self._empty_summary()
        try:
            raw  = await self._call(VISIT_SUMMARY_PROMPT.format(full_transcript=full_transcript), "generate_summary")
            data = self._parse_json(raw, "generate_summary")
            return {
                "title":        data.get("title", "Medical Visit"),
                "diagnosis":    data.get("diagnosis", ""),
                "medications":  data.get("medications", [])  if isinstance(data.get("medications"),  list) else [],
                "instructions": data.get("instructions", []) if isinstance(data.get("instructions"), list) else [],
                "follow_up":    data.get("follow_up", ""),
                "key_points":   data.get("key_points", [])   if isinstance(data.get("key_points"),   list) else [],
            }
        except (GeminiRateLimitError, GeminiAuthError):
            raise
        except Exception as e:
            self._log_api_error("generate_summary", e)
            return self._empty_summary()

    async def translate_text(self, text: str, target_language: str) -> str:
        if not text or target_language not in SUPPORTED_LANGUAGES:
            return text
        try:
            raw = await self._call(
                TRANSLATION_PROMPT.format(
                    target_language=SUPPORTED_LANGUAGES[target_language], text=text
                ),
                "translate_text",
            )
            return raw.strip()
        except (GeminiRateLimitError, GeminiAuthError):
            raise
        except Exception as e:
            self._log_api_error("translate_text", e)
            return text

    # ── Legacy compat (used by old main.py path) ──────────────
    async def simplify_terms(self, transcript: str) -> List[Dict[str, str]]:
        result = await self.get_insights(transcript)
        return result.get("medical_terms", [])

    async def suggest_questions(self, full_transcript: str) -> List[str]:
        result = await self.get_insights(full_transcript)
        return result.get("suggested_questions", [])

    async def explain_question(self, question: str, context: str = "") -> str:
        """Return a plain-English explanation of why a question matters and what to expect."""
        try:
            raw = await self._call(
                QUESTION_EXPLANATION_PROMPT.format(
                    question=question,
                    context=context[-1500:] if context else "No context available."
                ),
                "explain_question",
            )
            return raw.strip()
        except (GeminiRateLimitError, GeminiAuthError):
            raise
        except Exception as e:
            self._log_api_error("explain_question", e)
            return "This is a great question to ask your doctor. Listen carefully to their answer and don't hesitate to ask for clarification."
