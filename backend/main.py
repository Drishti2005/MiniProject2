# TEAM: Backend Infrastructure
# FastAPI application with WebSocket and REST API endpoints
# Orchestrates communication between Frontend and AI Integration

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
import os
import sys
from dotenv import load_dotenv
import logging
import asyncio
from typing import Dict

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
# Add parent directory to path to import ai-service
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Load environment variables FIRST
load_dotenv()

# Validate required environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Use SQLite-compatible database service based on DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    from database_sqlite import DatabaseService
else:
    from database import DatabaseService

from models import *
from performance import monitor_performance, PerformanceTimer
from security import (
    sanitize_text_input, 
    validate_websocket_message, 
    SanitizingLogger,
    ensure_no_audio_storage
)

# Configure logging with sanitization BEFORE importing AI service
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
)
logger = SanitizingLogger(__name__)

# Import AI service — new engine in src/ai_engine with Gemini + Groq support
# Falls back gracefully through providers based on .env configuration
try:
    src_path = os.path.join(parent_dir, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    from ai_engine import create_ai_service as _create_ai_service
    logger.info("AI engine loaded (Gemini + Groq with auto-fallback)")
    _USE_NEW_ENGINE = True
except Exception as _engine_err:
    logger.warning(f"New AI engine unavailable ({_engine_err}), falling back to legacy service")
    _USE_NEW_ENGINE = False
    # Legacy fallback chain
    try:
        from ai_service.gemini_service import GeminiService
        logger.info("Using legacy Gemini AI service")
    except ImportError:
        try:
            from ai_service.gemini_service_mock import GeminiService
            logger.info("Using MOCK Gemini AI service (for testing)")
        except ImportError:
            ai_service_path = os.path.join(parent_dir, 'ai-service')
            if ai_service_path not in sys.path:
                sys.path.insert(0, ai_service_path)
            from gemini_service_mock import GeminiService
            logger.info("Using MOCK Gemini AI service (fallback)")

# Check if we're running in test mode
import sys
TESTING = 'pytest' in sys.modules or 'unittest' in sys.modules

if not TESTING:
    if not GEMINI_API_KEY and not os.getenv("GROQ_API_KEY"):
        logger.critical("At least one AI API key is required: GEMINI_API_KEY or GROQ_API_KEY")
        sys.exit(1)

    if not DATABASE_URL:
        logger.critical("DATABASE_URL environment variable is required")
        sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="Sidekick Medical Assistant API",
    description="Real-time AI-powered medical appointment assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
if TESTING:
    db = DatabaseService(DATABASE_URL or "sqlite:///test.db")
    if _USE_NEW_ENGINE:
        try:
            gemini = _create_ai_service()
        except Exception:
            from ai_service.gemini_service_mock import GeminiService
            gemini = GeminiService("test-key")
    else:
        gemini = GeminiService(GEMINI_API_KEY or "test-key")
else:
    db = DatabaseService(DATABASE_URL)
    if _USE_NEW_ENGINE:
        gemini = _create_ai_service()
    else:
        gemini = GeminiService(GEMINI_API_KEY)

# Store active WebSocket connections and their session IDs
active_connections: Dict[WebSocket, str] = {}


# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on application startup"""
    try:
        await db.init_db()
        logger.info("Application started successfully")
    except Exception as e:
        logger.critical(f"Failed to start application: {e}")
        sys.exit(1)


# Serve frontend static files (only if frontend directory exists)
import os
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")
else:
    logger.warning("Frontend directory not found - static file serving disabled")


# REST API Endpoints
@app.get("/")
async def serve_frontend():
    """Serve the main application HTML page"""
    try:
        frontend_index = os.path.join(frontend_dir, "index.html")
        if os.path.exists(frontend_index):
            return FileResponse(frontend_index)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Frontend not found")
    except Exception as e:
        logger.error(f"Failed to serve frontend: {e}")
        raise HTTPException(status_code=500, detail="Failed to load application")


@app.get("/history")
async def serve_history():
    """Serve the session history HTML page"""
    try:
        history_page = os.path.join(frontend_dir, "history.html")
        if os.path.exists(history_page):
            return FileResponse(history_page)
        else:
            raise HTTPException(status_code=404, detail="History page not found")
    except Exception as e:
        logger.error(f"Failed to serve history: {e}")
        raise HTTPException(status_code=500, detail="Failed to load history page")

@app.get("/api/sessions")
async def list_sessions():
    """Return list of all sessions"""
    try:
        sessions = await db.get_all_sessions()
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Return full session details including transcript and summary"""
    try:
        session_details = await db.get_session_details(session_id)
        
        if not session_details:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session details")


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all related data"""
    try:
        # Check if session exists first
        session_details = await db.get_session_details(session_id)
        if not session_details:
            raise HTTPException(status_code=404, detail="Session not found")
        
        await db.delete_session(session_id)
        return {"status": "deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


# WebSocket Endpoint
@app.websocket("/ws/session")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication

    Handles:
    - Session creation on connection
    - Transcript processing
    - AI service calls (simplification, questions, translation)
    - Summary generation on session end
    """
    await websocket.accept()
    session_id = None
    
    try:
        # Create new session in database
        language = "en"  # Default language, can be updated by client
        session_id = await db.create_session(language)
        active_connections[websocket] = session_id
        
        logger.info(f"WebSocket connected, session created: {session_id}")
        
        # Send session ID to client
        await websocket.send_json({
            "type": "session_created",
            "session_id": session_id
        })
        
        # Accumulate transcript for context
        full_transcript = []
        session_language = language  # tracks current language, updated by language_change
        
        while True:
            # Receive message from frontend
            message = await websocket.receive_json()
            message_type = message.get("type")
            
            logger.debug(f"Received message type: {message_type} for session {session_id}")
            
            if message_type == "transcript":
                session_language = await handle_transcript(websocket, session_id, message, full_transcript, session_language)

            elif message_type == "end_session":
                await handle_end_session(websocket, session_id, full_transcript)
                break

            elif message_type == "ping":
                # Heartbeat — respond with pong
                await websocket.send_json({"type": "pong"})

            elif message_type == "language_change":
                # Update session language so future translations use the right target
                new_lang = message.get("language", "en")
                session_language = new_lang
                logger.info(f"Language changed to {new_lang} for session {session_id}")

            elif message_type == "question_ask":
                # Patient clicked a suggested question — get AI explanation for it
                await handle_question_ask(websocket, session_id, message, full_transcript, session_language)

            elif message_type == "doctor_reply":
                # Doctor typed/spoke a reply to a patient question — simplify + translate it
                await handle_doctor_reply(websocket, session_id, message, session_language)

            else:
                # Unknown message type — log but don't error-out the session
                logger.warning(f"Unknown message type: {message_type}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
        if session_id:
            try:
                await db.end_session(session_id)
            except Exception as e:
                logger.error(f"Failed to end session on disconnect: {e}")
    
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "An error occurred processing your request"
            })
        except:
            pass
    
    finally:
        # Clean up connection
        if websocket in active_connections:
            del active_connections[websocket]


async def handle_transcript(websocket: WebSocket, session_id: str, message: dict, full_transcript: list, session_language: str = "en") -> str:
    """
    Handle transcript message. Returns the (possibly updated) session_language.
    """
    try:
        msg_language = message.get("language", session_language)
        message["language"] = msg_language

        is_valid, error_msg = validate_websocket_message(message)
        if not is_valid:
            logger.warning(f"Invalid WebSocket message: {error_msg}")
            await websocket.send_json({"type": "error", "message": error_msg})
            return session_language

        transcript_msg = TranscriptMessage(**message)
        text     = sanitize_text_input(transcript_msg.text)
        language = transcript_msg.language

        # Sync session_language with what the client sends
        if language and language != "en":
            session_language = language

        if not text:
            return session_language

        # Store transcript chunk
        await db.add_transcript_chunk(session_id, text)
        full_transcript.append(text)

        # ── Single combined LLM call ──────────────────────────
        # Returns: { medical_terms, suggested_questions, session_summary }
        insights = await gemini.get_insights(text)

        medical_terms       = insights.get("medical_terms", [])
        suggested_questions = insights.get("suggested_questions", [])

        # ── Emit Terms Explained ──────────────────────────────
        if medical_terms:
            for t in medical_terms:
                if isinstance(t, dict) and "term" in t and "explanation" in t:
                    await db.add_simplification(session_id, t["term"], t["explanation"])

            await websocket.send_json({
                "type":  "simplification",
                "terms": medical_terms,
            })

        # ── Translation: translate the FULL transcript phrase ─
        # This gives a proper bilingual transcript, not just term snippets
        if language != "en":
            translated_phrase = await gemini.translate_text(text, language)
            if translated_phrase and translated_phrase != text:
                await websocket.send_json({
                    "type":     "transcript_translation",
                    "original": text,
                    "translated": translated_phrase,
                    "language": language,
                })

        # ── Emit Patient Prompts ──────────────────────────────
        if suggested_questions:
            # If non-English, translate each question so patient can read/hear it
            if language != "en":
                bilingual_questions = []
                for q in suggested_questions:
                    translated_q = await gemini.translate_text(q, language)
                    bilingual_questions.append({
                        "english":    q,
                        "translated": translated_q if translated_q and translated_q != q else None,
                        "language":   language,
                    })
                await websocket.send_json({
                    "type":        "questions",
                    "suggestions": bilingual_questions,
                    "bilingual":   True,
                })
            else:
                await websocket.send_json({
                    "type":        "questions",
                    "suggestions": suggested_questions,
                    "bilingual":   False,
                })

        # ── Emit session_info update (phrase + AI request counts) ─
        await websocket.send_json({
            "type":         "session_info",
            "phrase_count": len(full_transcript),
            "ai_requests":  len(full_transcript),
        })
        return session_language

    except ValidationError as e:
        logger.warning(f"Invalid transcript message format: {e}")
        await websocket.send_json({"type": "error", "message": "Invalid message format"})
        return session_language

    except Exception as e:
        logger.error(f"Error handling transcript: {e}", exc_info=True)
        await websocket.send_json({
            "type":    "ai_error",
            "message": "AI analysis temporarily unavailable. Transcription continues.",
        })
        return session_language


async def handle_end_session(websocket: WebSocket, session_id: str, full_transcript: list):
    """
    Handle end_session message from frontend
    
    - Compile full transcript
    - Generate visit summary
    - Store summary in database
    - Send summary to frontend
    """
    try:
        logger.info(f"Ending session {session_id}")
        
        # Compile full transcript
        full_text = " ".join(full_transcript)
        
        if not full_text.strip():
            logger.warning(f"No transcript available for session {session_id}")
            await websocket.send_json({
                "type": "error",
                "message": "No transcript available to summarize"
            })
            await db.end_session(session_id)
            return
        
        # Generate summary using Gemini
        summary = await gemini.generate_summary(full_text)
        
        if summary:
            # Store summary in database
            await db.save_summary(session_id, summary)
            
            # Send summary to frontend
            await websocket.send_json({
                "type": "summary",
                "data": summary
            })
            
            logger.info(f"Summary generated and sent for session {session_id}")
        else:
            logger.warning(f"Failed to generate summary for session {session_id}")
            await websocket.send_json({
                "type": "error",
                "message": "Failed to generate summary"
            })
        
        # Mark session as ended
        await db.end_session(session_id)
    
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Failed to end session"
        })
        # Still try to end the session
        try:
            await db.end_session(session_id)
        except:
            pass


async def handle_question_ask(websocket: WebSocket, session_id: str, message: dict, full_transcript: list, session_language: str):
    """
    Patient clicked a suggested question.
    1. Store it as a transcript chunk (so it's part of the session record)
    2. Ask the AI to explain the answer in plain language
    3. Send back a question_explanation event
    4. Translate if non-English
    """
    try:
        question = message.get("question", "").strip()
        if not question:
            return

        # Add to transcript so the summary includes it
        full_transcript.append(f"[Patient question] {question}")
        await db.add_transcript_chunk(session_id, f"[Patient question] {question}")

        # Ask AI to explain the answer
        explanation = await gemini.explain_question(question, " ".join(full_transcript))

        await websocket.send_json({
            "type":        "question_explanation",
            "question":    question,
            "explanation": explanation,
        })

        # Translate explanation if non-English
        if session_language != "en" and explanation:
            translated = await gemini.translate_text(explanation, session_language)
            if translated and translated != explanation:
                await websocket.send_json({
                    "type":        "question_explanation_translated",
                    "question":    question,
                    "explanation": translated,
                    "language":    session_language,
                })

    except Exception as e:
        logger.error(f"Error handling question_ask: {e}", exc_info=True)
        await websocket.send_json({
            "type":    "ai_error",
            "message": "Could not generate explanation for that question.",
        })


async def handle_doctor_reply(websocket: WebSocket, session_id: str, message: dict, session_language: str):
    """
    Doctor typed/spoke a reply to a patient question.
    1. Store it as a transcript chunk
    2. Simplify any medical terms in the reply
    3. Translate if non-English
    4. Send back doctor_reply_simplified event
    """
    try:
        reply    = message.get("reply", "").strip()
        question = message.get("question", "")
        if not reply:
            return

        await db.add_transcript_chunk(session_id, f"[Doctor reply] {reply}")

        # Simplify the doctor's reply
        insights = await gemini.get_insights(reply)
        terms    = insights.get("medical_terms", [])

        # Translate the reply if non-English — include in the same event
        translated_reply = None
        if session_language != "en":
            translated_reply = await gemini.translate_text(reply, session_language)
            if translated_reply == reply:
                translated_reply = None

        await websocket.send_json({
            "type":             "doctor_reply_simplified",
            "question":         question,
            "reply":            reply,
            "reply_translated": translated_reply,
            "language":         session_language,
            "terms":            terms,
        })

    except Exception as e:
        logger.error(f"Error handling doctor_reply: {e}", exc_info=True)
        await websocket.send_json({
            "type":    "ai_error",
            "message": "Could not simplify the doctor's reply.",
        })


# TTS proxy — fetches audio from Google Translate and streams it back
# Avoids CORS/autoplay issues when playing from the frontend
@app.get("/api/tts")
async def tts_proxy(text: str, lang: str = "hi"):
    """Proxy Google Translate TTS audio to avoid CORS issues in the browser."""
    import httpx
    from fastapi.responses import StreamingResponse

    # Validate lang code — only allow 2-3 char ISO codes
    import re
    if not re.match(r'^[a-z]{2,3}(-[A-Za-z]{2,4})?$', lang):
        raise HTTPException(status_code=400, detail="Invalid language code")

    # Truncate to 200 chars (GT limit)
    text = text[:200]

    url = "https://translate.google.com/translate_tts"
    params = {"ie": "UTF-8", "q": text, "tl": lang, "client": "tw-ob"}
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Sidekick/1.0)"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params, headers=headers)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="TTS service unavailable")
            return StreamingResponse(
                iter([resp.content]),
                media_type="audio/mpeg",
                headers={"Cache-Control": "no-store"},
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="TTS request timed out")
    except Exception as e:
        logger.error(f"TTS proxy error: {e}")
        raise HTTPException(status_code=502, detail="TTS unavailable")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Sidekick Medical Assistant",
        "version": "1.0.0"
    }


@app.get("/api/health/ai")
async def ai_health():
    """Returns which AI provider is currently active."""
    provider = getattr(gemini, "active_provider", type(gemini).__name__)
    return {
        "status":   "ok",
        "provider": provider,
        "engine":   "new" if _USE_NEW_ENGINE else "legacy",
    }
