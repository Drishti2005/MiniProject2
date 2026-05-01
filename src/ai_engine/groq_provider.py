"""
Groq AI provider — fallback when Gemini returns 403/429.
Uses llama-3.3-70b-versatile (fast, free-tier friendly).
Logs all errors to ai_debug.log.
"""

import asyncio
import logging
import time
from typing import Dict, List

from .base import BaseAIService, SUPPORTED_LANGUAGES, _write_debug
from .prompts import COMBINED_INSIGHT_PROMPT, VISIT_SUMMARY_PROMPT, TRANSLATION_PROMPT, QUESTION_EXPLANATION_PROMPT

logger = logging.getLogger(__name__)

GROQ_MODEL  = "llama-3.3-70b-versatile"
TEMPERATURE = 0.3
MAX_TOKENS  = 1024
API_TIMEOUT = 60   # increased for Render free tier cold starts


class GroqProvider(BaseAIService):
    """Groq-backed AI service (fallback provider)."""

    _provider_name = "Groq"

    def __init__(self, api_key: str):
        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid or missing GROQ_API_KEY")
        try:
            from groq import Groq
            self._client = Groq(api_key=api_key)
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")
        logger.info(f"GroqProvider ready (model={GROQ_MODEL})")
        _write_debug("INFO", "Groq", "init", f"GroqProvider initialised with model={GROQ_MODEL}")

    async def _call(self, prompt: str, op: str) -> str:
        t0 = time.time()
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self._client.chat.completions.create,
                    model=GROQ_MODEL,
                    messages=[{"role": "user", "content": self._sanitize(prompt)}],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                ),
                timeout=API_TIMEOUT,
            )
            self._log_api_success(op, time.time() - t0)
            return response.choices[0].message.content
        except asyncio.TimeoutError as e:
            self._log_api_error(op, e)
            raise RuntimeError(f"Groq timeout on {op}") from e
        except Exception as e:
            self._log_api_error(op, e)
            raise RuntimeError(f"Groq error on {op}: {e}") from e

    # ── Public interface ──────────────────────────────────────

    async def get_insights(self, transcript: str) -> Dict:
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
        except Exception as e:
            self._log_api_error("translate_text", e)
            return text

    # ── Legacy compat ─────────────────────────────────────────
    async def simplify_terms(self, transcript: str) -> List[Dict[str, str]]:
        result = await self.get_insights(transcript)
        return result.get("medical_terms", [])

    async def suggest_questions(self, full_transcript: str) -> List[str]:
        result = await self.get_insights(full_transcript)
        return result.get("suggested_questions", [])

    async def explain_question(self, question: str, context: str = "") -> str:
        try:
            raw = await self._call(
                QUESTION_EXPLANATION_PROMPT.format(
                    question=question,
                    context=context[-1500:] if context else "No context available."
                ),
                "explain_question",
            )
            return raw.strip()
        except Exception as e:
            self._log_api_error("explain_question", e)
            return "This is a great question to ask your doctor. Listen carefully to their answer."
