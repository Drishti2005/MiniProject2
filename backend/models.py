# TEAM: Backend Infrastructure
# Pydantic models for WebSocket messages and database entities
# This file defines the contract between Frontend, Backend, and AI Integration

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# WebSocket Message Models
class TranscriptMessage(BaseModel):
    """Message sent from Frontend when speech is recognized"""
    type: str = "transcript"
    text: str
    language: str = "en"

class SimplificationTerm(BaseModel):
    """A single medical term with its explanation"""
    term: str
    explanation: str

class SimplificationMessage(BaseModel):
    """Message sent from Backend to Frontend with simplified terms"""
    type: str = "simplification"
    terms: List[SimplificationTerm]

class QuestionsMessage(BaseModel):
    """Message sent from Backend to Frontend with suggested questions"""
    type: str = "questions"
    suggestions: List[str]

class TranslationMessage(BaseModel):
    """Message sent from Backend to Frontend with translated text"""
    type: str = "translation"
    text: str

class SummaryData(BaseModel):
    """Structured visit summary data"""
    title: str
    diagnosis: str
    medications: List[str]
    instructions: List[str]
    follow_up: str
    key_points: List[str]

class SummaryMessage(BaseModel):
    """Message sent from Backend to Frontend with visit summary"""
    type: str = "summary"
    data: SummaryData

class ErrorMessage(BaseModel):
    """Message sent from Backend to Frontend when an error occurs"""
    type: str = "error"
    message: str

# Database Models
class Session(BaseModel):
    """Database model for a medical appointment session"""
    id: UUID
    title: Optional[str]
    language: str
    created_at: datetime
    ended_at: Optional[datetime]

class TranscriptChunk(BaseModel):
    """Database model for a transcript chunk"""
    id: int
    session_id: UUID
    text: str
    timestamp: datetime

class Simplification(BaseModel):
    """Database model for a medical term simplification"""
    id: int
    session_id: UUID
    term: str
    explanation: str
    timestamp: datetime

class Summary(BaseModel):
    """Database model for a visit summary"""
    id: int
    session_id: UUID
    title: Optional[str]
    diagnosis: Optional[str]
    medications: List[str]
    instructions: List[str]
    follow_up: Optional[str]
    key_points: List[str]
    created_at: datetime

class SessionDetail(BaseModel):
    """Complete session data including all related records"""
    session: Session
    transcript: List[TranscriptChunk]
    simplifications: List[Simplification]
    summary: Optional[Summary]
