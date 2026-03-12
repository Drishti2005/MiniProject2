"""
Gemini AI Service for Sidekick Medical Appointment Assistant.

This module provides the core AI functionality including:
- Medical terminology simplification
- Question suggestion generation
- Visit summary creation
- Translation services
- Rate limiting and error handling
"""

import asyncio
import json
import logging
import re
import time
from collections import deque
from typing import Dict, List

import google.generativeai as genai

from .config import (
    GEMINI_MODEL,
    MAX_REQUESTS_PER_MINUTE,
    RATE_LIMIT_WINDOW_SECONDS,
    API_TIMEOUT_SECONDS,
    MAX_RETRY_ATTEMPTS,
    RETRY_BACKOFF_SECONDS,
    SLOW_REQUEST_THRESHOLD_SECONDS,
    SUPPORTED_LANGUAGES,
    TEMPERATURE,
    MAX_TOKENS,
    SENSITIVE_PATTERNS,
    LOG_API_CALLS,
    LOG_SLOW_REQUESTS,
    LOG_ERRORS,
)
from .prompts import (
    SIMPLIFICATION_PROMPT,
    QUESTION_SUGGESTION_PROMPT,
    VISIT_SUMMARY_PROMPT,
    TRANSLATION_PROMPT,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter with request queueing."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a request, waiting if necessary."""
        async with self.lock:
            now = time.time()

            # Remove requests outside the time window
            while self.requests and self.requests[0] < now - self.window_seconds:
                self.requests.popleft()

            # If at capacity, wait until oldest request expires
            if len(self.requests) >= self.max_requests:
                wait_time = self.requests[0] + self.window_seconds - now
                if wait_time > 0:
                    logger.info(f"Rate limit reached. Queueing request for {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    return await self.acquire()

            # Record this request
            self.requests.append(now)
            logger.debug(
                f"Rate limiter: {len(self.requests)}/{self.max_requests} requests in window")


class GeminiService:
    """
    Service for interacting with Google Gemini API.

    Provides medical terminology simplification, question suggestions,
    visit summaries, and translation services with rate limiting,
    error handling, and performance monitoring.
    """

    def __init__(self, api_key: str):
        """
        Initialize Gemini service.

        Args:
            api_key: Google Gemini API key

        Raises:
            ValueError: If API key is missing or invalid
        """
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required")

        # Validate API key format (basic check)
        if not self._validate_api_key(api_key):
            raise ValueError("Invalid GEMINI_API_KEY format")

        # Configure Gemini
        genai.configure(api_key=api_key)

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                "temperature": TEMPERATURE,
                "max_output_tokens": MAX_TOKENS,
            }
        )

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=MAX_REQUESTS_PER_MINUTE,
            window_seconds=RATE_LIMIT_WINDOW_SECONDS
        )

        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.slow_requests = 0

        logger.info(f"GeminiService initialized with model {GEMINI_MODEL}")

    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key format."""
        # Basic validation: non-empty, reasonable length
        return bool(api_key) and len(api_key) > 10

    def _sanitize_prompt(self, text: str) -> str:
        """
        Sanitize prompt to remove sensitive patient identifiers.

        Args:
            text: Input text

        Returns:
            Sanitized text
        """
        sanitized = text
        for pattern in SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, "[REDACTED]", sanitized, flags=re.IGNORECASE)
        return sanitized

    async def _call_api_with_retry(
        self,
        prompt: str,
        operation: str
    ) -> str:
        """
        Call Gemini API with retry logic and error handling.

        Args:
            prompt: Prompt to send to API
            operation: Operation name for logging

        Returns:
            API response text

        Raises:
            Exception: If all retry attempts fail
        """
        start_time = time.time()

        for attempt in range(MAX_RETRY_ATTEMPTS):
            try:
                # Acquire rate limit permission
                await self.rate_limiter.acquire()

                # Sanitize prompt
                sanitized_prompt = self._sanitize_prompt(prompt)

                # Make API call with timeout
                if LOG_API_CALLS:
                    logger.info(
                        f"API call: {operation} (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS})")

                # Use asyncio.wait_for for timeout
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.model.generate_content,
                        sanitized_prompt
                    ),
                    timeout=API_TIMEOUT_SECONDS
                )

                # Track performance
                elapsed = time.time() - start_time
                self.request_count += 1
                self.total_response_time += elapsed

                if elapsed > SLOW_REQUEST_THRESHOLD_SECONDS:
                    self.slow_requests += 1
                    if LOG_SLOW_REQUESTS:
                        logger.warning(f"Slow request: {operation} took {elapsed:.2f}s")

                if LOG_API_CALLS:
                    logger.info(f"API response: {operation} completed in {elapsed:.2f}s")

                return response.text

            except asyncio.TimeoutError:
                logger.error(f"Timeout on {operation} (attempt {attempt + 1})")
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS[attempt])
                else:
                    raise Exception(f"API timeout after {MAX_RETRY_ATTEMPTS} attempts")

            except Exception as e:
                logger.error(f"Error on {operation} (attempt {attempt + 1}): {str(e)}")
                if attempt < MAX_RETRY_ATTEMPTS - 1:
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS[attempt])
                else:
                    if LOG_ERRORS:
                        logger.error(
                            f"API call failed after {MAX_RETRY_ATTEMPTS} attempts: {str(e)}")
                    raise Exception(f"API error: {str(e)}")

        raise Exception(f"Failed to complete {operation} after {MAX_RETRY_ATTEMPTS} attempts")

    def _parse_json_response(self, response_text: str, operation: str) -> Dict:
        """
        Parse JSON response from API.

        Args:
            response_text: Raw API response
            operation: Operation name for error messages

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {operation}: {str(e)}")
            logger.error(f"Response text: {response_text[:200]}")
            raise ValueError(f"Failed to parse JSON response: {str(e)}")

    async def simplify_terms(self, transcript: str) -> List[Dict[str, str]]:
        """
        Simplify medical terms in transcript.

        Args:
            transcript: Transcript chunk containing potential medical terms

        Returns:
            List of dicts with 'term' and 'explanation' keys

        Example:
            >>> terms = await service.simplify_terms("Patient has hypertension")
            >>> print(terms)
            [{"term": "hypertension", "explanation": "high blood pressure"}]
        """
        if not transcript or not transcript.strip():
            return []

        try:
            prompt = SIMPLIFICATION_PROMPT.format(transcript=transcript)
            response_text = await self._call_api_with_retry(prompt, "simplify_terms")

            data = self._parse_json_response(response_text, "simplify_terms")

            # Validate response structure
            if "terms" not in data:
                logger.warning("Missing 'terms' field in simplification response")
                return []

            terms = data["terms"]

            # Validate each term has required fields
            validated_terms = []
            for term in terms:
                if isinstance(term, dict) and "term" in term and "explanation" in term:
                    validated_terms.append({
                        "term": term["term"],
                        "explanation": term["explanation"]
                    })

            logger.info(f"Simplified {len(validated_terms)} medical terms")
            return validated_terms

        except Exception as e:
            logger.error(f"Error in simplify_terms: {str(e)}")
            return []

    async def suggest_questions(self, full_transcript: str) -> List[str]:
        """
        Generate question suggestions based on conversation.

        Args:
            full_transcript: Complete conversation transcript

        Returns:
            List of 2-3 suggested questions

        Example:
            >>> questions = await service.suggest_questions(transcript)
            >>> print(questions)
            ["What are the side effects?", "How long until I feel better?"]
        """
        if not full_transcript or not full_transcript.strip():
            return []

        # Check for minimum context (rough heuristic: at least 50 words)
        word_count = len(full_transcript.split())
        if word_count < 50:
            logger.info(f"Insufficient context for questions ({word_count} words)")
            return []

        try:
            prompt = QUESTION_SUGGESTION_PROMPT.format(full_transcript=full_transcript)
            response_text = await self._call_api_with_retry(prompt, "suggest_questions")

            data = self._parse_json_response(response_text, "suggest_questions")

            # Validate response structure
            if "questions" not in data:
                logger.warning("Missing 'questions' field in response")
                return []

            questions = data["questions"]

            # Validate questions are strings and limit to 2-3
            validated_questions = [
                q for q in questions
                if isinstance(q, str) and q.strip()
            ][:3]

            logger.info(f"Generated {len(validated_questions)} question suggestions")
            return validated_questions

        except Exception as e:
            logger.error(f"Error in suggest_questions: {str(e)}")
            return []

    async def generate_summary(self, full_transcript: str) -> Dict:
        """
        Generate structured visit summary.

        Args:
            full_transcript: Complete conversation transcript

        Returns:
            Dict with keys: title, diagnosis, medications, instructions,
            follow_up, key_points

        Example:
            >>> summary = await service.generate_summary(transcript)
            >>> print(summary["title"])
            "Hypertension Follow-up"
        """
        if not full_transcript or not full_transcript.strip():
            return self._empty_summary()

        try:
            prompt = VISIT_SUMMARY_PROMPT.format(full_transcript=full_transcript)
            response_text = await self._call_api_with_retry(prompt, "generate_summary")

            data = self._parse_json_response(response_text, "generate_summary")

            # Validate and normalize summary structure
            summary = {
                "title": data.get(
                    "title",
                    "Medical Visit"),
                "diagnosis": data.get(
                    "diagnosis",
                    ""),
                "medications": data.get(
                    "medications",
                    []) if isinstance(
                    data.get("medications"),
                    list) else [],
                "instructions": data.get(
                        "instructions",
                        []) if isinstance(
                            data.get("instructions"),
                            list) else [],
                "follow_up": data.get(
                                "follow_up",
                                ""),
                "key_points": data.get(
                    "key_points",
                    []) if isinstance(
                    data.get("key_points"),
                    list) else [],
            }

            logger.info(f"Generated visit summary: {summary['title']}")
            return summary

        except Exception as e:
            logger.error(f"Error in generate_summary: {str(e)}")
            return self._empty_summary()

    def _empty_summary(self) -> Dict:
        """Return empty summary structure."""
        return {
            "title": "Medical Visit",
            "diagnosis": "",
            "medications": [],
            "instructions": [],
            "follow_up": "",
            "key_points": []
        }

    async def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code (es, hi, zh, fr, ar)

        Returns:
            Translated text

        Raises:
            ValueError: If language not supported

        Example:
            >>> translated = await service.translate_text("High blood pressure", "es")
            >>> print(translated)
            "Presión arterial alta"
        """
        if not text or not text.strip():
            return ""

        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {target_language}. "
                f"Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"
            )

        try:
            language_name = SUPPORTED_LANGUAGES[target_language]
            prompt = TRANSLATION_PROMPT.format(
                target_language=language_name,
                text=text
            )

            response_text = await self._call_api_with_retry(prompt, "translate_text")

            # Translation response is plain text, not JSON
            translated = response_text.strip()

            logger.info(f"Translated text to {language_name}")
            return translated

        except Exception as e:
            logger.error(f"Error in translate_text: {str(e)}")
            return text  # Return original text on error

    def get_performance_stats(self) -> Dict:
        """
        Get performance statistics.

        Returns:
            Dict with performance metrics
        """
        avg_response_time = (
            self.total_response_time / self.request_count
            if self.request_count > 0
            else 0
        )

        return {
            "total_requests": self.request_count,
            "average_response_time": round(avg_response_time, 2),
            "slow_requests": self.slow_requests,
            "slow_request_percentage": round(
                (self.slow_requests / self.request_count * 100)
                if self.request_count > 0
                else 0,
                2
            )
        }
