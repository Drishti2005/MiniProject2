# MOCK AI Service for testing backend
# This is a temporary mock until the AI Integration team implements the real service
#
# IMPORTANT FOR AI TEAM:
# - The real service should be in: ai-service/gemini_service.py
# - This mock is in: ai-service/gemini_service_mock.py
# - backend/main.py will automatically use the real service when available
# - This mock will remain for testing purposes
#
# The real service should implement the same interface:
# - __init__(self, api_key: str)
# - async def simplify_terms(self, transcript: str) -> Dict
# - async def suggest_questions(self, full_transcript: str) -> Dict
# - async def generate_summary(self, full_transcript: str) -> Dict
# - async def translate_text(self, text: str, target_language: str) -> str

import asyncio
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Mock Gemini service for testing backend functionality"""

    def __init__(self, api_key: str):
        """Initialize mock Gemini service"""
        self.api_key = api_key
        logger.info("Mock Gemini service initialized")

    async def simplify_terms(self, transcript: str) -> Dict:
        """
        Mock: Identify medical terms and provide explanations
        
        Returns mock simplifications for testing
        """
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Mock medical term detection
        terms = []
        if "blood pressure" in transcript.lower() or "hypertension" in transcript.lower():
            terms.append({
                "term": "hypertension",
                "explanation": "high blood pressure"
            })
        
        if "diabetes" in transcript.lower():
            terms.append({
                "term": "diabetes",
                "explanation": "condition where blood sugar levels are too high"
            })
        
        if "ace inhibitor" in transcript.lower():
            terms.append({
                "term": "ACE inhibitor",
                "explanation": "medication that helps lower blood pressure"
            })
        
        logger.info(f"Mock simplification: found {len(terms)} terms")
        return {"terms": terms}

    async def suggest_questions(self, full_transcript: str) -> Dict:
        """
        Mock: Generate clarification questions
        
        Returns mock questions for testing
        """
        await asyncio.sleep(0.1)  # Simulate API delay
        
        questions = [
            "What are the side effects of this medication?",
            "How often should I check my blood pressure?",
            "When should I schedule a follow-up appointment?"
        ]
        
        logger.info(f"Mock questions: generated {len(questions)} questions")
        return {"questions": questions}

    async def generate_summary(self, full_transcript: str) -> Dict:
        """
        Mock: Generate visit summary
        
        Returns mock summary for testing
        """
        await asyncio.sleep(0.2)  # Simulate API delay
        
        summary = {
            "title": "Medical Consultation Summary",
            "diagnosis": "Elevated blood pressure requiring medication",
            "medications": ["ACE inhibitor", "Low-dose aspirin"],
            "instructions": [
                "Take medication daily with food",
                "Monitor blood pressure at home",
                "Reduce salt intake"
            ],
            "follow_up": "Return in 2 weeks for blood pressure check",
            "key_points": [
                "Blood pressure is elevated",
                "Starting new medication",
                "Lifestyle changes recommended"
            ]
        }
        
        logger.info("Mock summary: generated visit summary")
        return summary

    async def translate_text(self, text: str, target_language: str) -> str:
        """
        Mock: Translate text to target language
        
        Returns mock translation for testing
        """
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Mock translation (just adds language prefix)
        translations = {
            "es": f"[ES] {text}",  # Spanish
            "hi": f"[HI] {text}",  # Hindi
            "zh": f"[ZH] {text}",  # Mandarin
            "fr": f"[FR] {text}",  # French
            "ar": f"[AR] {text}"   # Arabic
        }
        
        translated = translations.get(target_language, f"[{target_language.upper()}] {text}")
        logger.info(f"Mock translation: translated to {target_language}")
        return translated
