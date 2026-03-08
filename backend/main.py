# TEAM: Backend Infrastructure
# FastAPI application with WebSocket and REST API endpoints
# Orchestrates communication between Frontend and AI Integration

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path to import ai-service
sys.path.append('..')

from database import DatabaseService
from ai_service.gemini_service import GeminiService
from models import *

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Sidekick Medical Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = DatabaseService(os.getenv("DATABASE_URL"))
gemini = GeminiService(os.getenv("GEMINI_API_KEY"))

# Startup event
@app.on_event("startup")
async def startup():
    """Initialize database on application startup"""
    # TODO: Initialize database
    pass

# Serve frontend static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# REST API Endpoints
@app.get("/")
async def serve_frontend():
    """Serve the main application HTML page"""
    # TODO: Return frontend/index.html
    pass

@app.get("/api/sessions")
async def list_sessions():
    """Return list of all sessions"""
    # TODO: Get all sessions from database
    # TODO: Return in JSON format
    pass

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Return full session details including transcript and summary"""
    # TODO: Get session details from database
    # TODO: Return in JSON format
    pass

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all related data"""
    # TODO: Delete session from database
    # TODO: Return success status
    pass

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
    
    # TODO: Create new session in database
    session_id = None
    
    try:
        while True:
            # Receive message from frontend
            message = await websocket.receive_json()
            
            # TODO: Handle different message types
            if message["type"] == "transcript":
                # TODO: Store transcript in database
                # TODO: Call AI service for simplification
                # TODO: Call AI service for questions
                # TODO: If translation enabled, call AI service for translation
                # TODO: Send results back to frontend
                pass
            
            elif message["type"] == "end_session":
                # TODO: Compile full transcript
                # TODO: Call AI service for summary
                # TODO: Store summary in database
                # TODO: Send summary to frontend
                # TODO: End session in database
                break
    
    except WebSocketDisconnect:
        # TODO: End session if not already ended
        pass
    
    except Exception as e:
        # TODO: Log error
        # TODO: Send error message to frontend
        pass
