# TEAM: Backend Infrastructure
# FastAPI application with WebSocket and REST API endpoints
# Orchestrates communication between Frontend and AI Integration

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
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

# Import AI service - tries real service first, falls back to mock
try:
    # Try to import real AI service (from AI Integration team)
    from ai_service.gemini_service import GeminiService
    logger.info("Using REAL Gemini AI service")
except ImportError:
    try:
        # Fall back to mock service for testing
        from ai_service.gemini_service_mock import GeminiService
        logger.info("Using MOCK Gemini AI service (for testing)")
    except ImportError:
        # Try alternative import path for mock
        import sys
        import os
        ai_service_path = os.path.join(parent_dir, 'ai-service')
        if ai_service_path not in sys.path:
            sys.path.insert(0, ai_service_path)
        from gemini_service_mock import GeminiService
        logger.info("Using MOCK Gemini AI service (for testing)")

# Check if we're running in test mode
import sys
TESTING = 'pytest' in sys.modules or 'unittest' in sys.modules

if not TESTING:
    if not GEMINI_API_KEY:
        logger.critical("GEMINI_API_KEY environment variable is required")
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

# Initialize services - must be done after loading env vars
# Use SQLite-compatible database service
# For tests, use default values if env vars are missing
if TESTING:
    db = DatabaseService(DATABASE_URL or "sqlite:///test.db")
    gemini = GeminiService(GEMINI_API_KEY or "test-key")
else:
    db = DatabaseService(DATABASE_URL)
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


# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")


# REST API Endpoints
@app.get("/")
async def serve_frontend():
    """Serve the main application HTML page"""
    try:
        return FileResponse("frontend/index.html")
    except Exception as e:
        logger.error(f"Failed to serve frontend: {e}")
        raise HTTPException(status_code=500, detail="Failed to load application")


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
        
        while True:
            # Receive message from frontend
            message = await websocket.receive_json()
            message_type = message.get("type")
            
            logger.debug(f"Received message type: {message_type} for session {session_id}")
            
            if message_type == "transcript":
                await handle_transcript(websocket, session_id, message, full_transcript)
                
            elif message_type == "end_session":
                await handle_end_session(websocket, session_id, full_transcript)
                break
                
            else:
                # Unknown message type
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

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


async def handle_transcript(websocket: WebSocket, session_id: str, message: dict, full_transcript: list):
    """
    Handle transcript message from frontend
    
    - Store transcript in database
    - Call Gemini for simplification
    - Call Gemini for question suggestions
    - Handle translation if needed
    """
    with PerformanceTimer("handle_transcript", threshold_ms=2000):  # 2 second threshold
        try:
            # Validate message structure
            is_valid, error_msg = validate_websocket_message(message)
            if not is_valid:
                logger.warning(f"Invalid WebSocket message: {error_msg}")
                await websocket.send_json({
                    "type": "error",
                    "message": error_msg
                })
                return
            
            # Validate and sanitize message
            transcript_msg = TranscriptMessage(**message)
            text = sanitize_text_input(transcript_msg.text)
            language = transcript_msg.language
            
            # Store transcript chunk in database
            with PerformanceTimer("store_transcript", threshold_ms=500):
                await db.add_transcript_chunk(session_id, text)
            
            # Add to full transcript for context
            full_transcript.append(text)
            
            # Call Gemini for simplification
            with PerformanceTimer("gemini_simplify", threshold_ms=1500):
                simplifications = await gemini.simplify_terms(text)
            
            if simplifications and simplifications.get("terms"):
                # Store simplifications in database
                for term_data in simplifications["terms"]:
                    await db.add_simplification(
                        session_id,
                        term_data["term"],
                        term_data["explanation"]
                    )
                
                # Send simplifications to frontend
                await websocket.send_json({
                    "type": "simplification",
                    "terms": simplifications["terms"]
                })
                
                # Handle translation if non-English language
                if language != "en":
                    for term_data in simplifications["terms"]:
                        translated = await gemini.translate_text(
                            term_data["explanation"],
                            language
                        )
                        if translated:
                            await websocket.send_json({
                                "type": "translation",
                                "text": translated,
                                "original_term": term_data["term"]
                            })
            
            # Generate question suggestions if we have enough context
            if len(full_transcript) >= 3:
                questions = await gemini.suggest_questions(" ".join(full_transcript))
                
                if questions and questions.get("questions"):
                    await websocket.send_json({
                        "type": "questions",
                        "suggestions": questions["questions"]
                    })
        
        except ValidationError as e:
            logger.warning(f"Invalid transcript message format: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Invalid message format"
            })
        
        except Exception as e:
            logger.error(f"Error handling transcript: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Failed to process transcript"
            })


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


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Sidekick Medical Assistant",
        "version": "1.0.0"
    }
