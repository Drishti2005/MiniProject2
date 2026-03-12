# AI Service Package
"""
Gemini AI Service for Sidekick Medical Appointment Assistant.

This package provides AI-powered features including:
- Medical terminology simplification
- Question suggestion generation
- Visit summary creation
- Translation services
"""

from .gemini_service import GeminiService

__all__ = ['GeminiService']
__version__ = '1.0.0'
