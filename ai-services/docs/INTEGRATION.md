# Integration Guide

This guide explains how to integrate the Gemini AI service with the Sidekick Medical Appointment Assistant backend.

## Table of Contents

- [Overview](#overview)
- [File Structure](#file-structure)
- [Integration Steps](#integration-steps)
- [Backend Integration](#backend-integration)
- [WebSocket Integration](#websocket-integration)
- [Database Integration](#database-integration)
- [Testing Integration](#testing-integration)
- [Deployment](#deployment)

## Overview

The AI service integrates with the backend through:
1. **WebSocket handlers**: Process transcript chunks in real-time
2. **REST endpoints**: Generate summaries on session end
3. **Database service**: Store AI-generated content

## File Structure

### Copy These Files to Backend

```
.kiro/ai-task-implementation/
├── gemini_service.py          → backend/gemini_service.py
├── config.py                  → backend/config.py (or merge with existing)
├── prompts.py                 → backend/prompts.py
└── requirements.txt           → merge with backend/requirements.txt
```

### Update Backend Requirements

Add to `backend/requirements.txt`:

```txt
google-generativeai>=0.3.0
```

## Integration Steps

### Step 1: Copy Files

```bash
# From project root
cp .kiro/ai-task-implementation/gemini_service.py backend/
cp .kiro/ai-task-implementation/config.py backend/
cp .kiro/ai-task-implementation/prompts.py backend/
```

### Step 2: Update Environment Variables

Add to `.env`:

```bash
GEMINI_API_KEY=your_api_key_here
```

### Step 3: Initialize Service in Backend

In `backend/main.py`:

```python
import os
from fastapi import FastAPI
from gemini_service import GeminiService

app = FastAPI()

# Initialize Gemini service
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")

gemini_service = GeminiService(api_key=gemini_api_key)
```

## Backend Integration

### WebSocket Handler Integration

In `backend/main.py`, update WebSocket handler:

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
import json

@app.websocket("/ws/session")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Create session
    session_id = await db.create_session(language="en")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "transcript":
                await handle_transcript(websocket, session_id, data)
            
            elif message_type == "end_session":
                await handle_end_session(websocket, session_id)
                break
    
    except WebSocketDisconnect:
        await db.end_session(session_id)


async def handle_transcript(websocket: WebSocket, session_id: str, data: Dict):
    """Handle incoming transcript chunk."""
    transcript_text = data.get("text", "")
    language = data.get("language", "en")
    
    # Store transcript chunk
    await db.add_transcript_chunk(session_id, transcript_text)
    
    # Get medical term simplifications
    terms = await gemini_service.simplify_terms(transcript_text)
    
    if terms:
        # Store simplifications
        for term_data in terms:
            await db.add_simplification(
                session_id,
                term_data["term"],
                term_data["explanation"]
            )
        
        # Send to frontend
        await websocket.send_json({
            "type": "simplification",
            "terms": terms
        })
        
        # Translate if non-English
        if language != "en":
            for term_data in terms:
                try:
                    translated = await gemini_service.translate_text(
                        term_data["explanation"],
                        language
                    )
                    await websocket.send_json({
                        "type": "translation",
                        "text": translated
                    })
                except Exception as e:
                    print(f"Translation error: {e}")
    
    # Generate question suggestions (if enough context)
    full_transcript = await db.get_full_transcript(session_id)
    questions = await gemini_service.suggest_questions(full_transcript)
    
    if questions:
        await websocket.send_json({
            "type": "questions",
            "suggestions": questions
        })


async def handle_end_session(websocket: WebSocket, session_id: str):
    """Handle session end and generate summary."""
    # Get full transcript
    full_transcript = await db.get_full_transcript(session_id)
    
    # Generate summary
    summary = await gemini_service.generate_summary(full_transcript)
    
    # Store summary
    await db.save_summary(session_id, summary)
    
    # Send to frontend
    await websocket.send_json({
        "type": "summary",
        "data": summary
    })
    
    # End session
    await db.end_session(session_id)
```

### Error Handling

Add error handling wrapper:

```python
async def handle_transcript(websocket: WebSocket, session_id: str, data: Dict):
    """Handle incoming transcript chunk with error handling."""
    try:
        transcript_text = data.get("text", "")
        language = data.get("language", "en")
        
        # Store transcript chunk
        await db.add_transcript_chunk(session_id, transcript_text)
        
        # Get simplifications
        try:
            terms = await gemini_service.simplify_terms(transcript_text)
            if terms:
                # Process terms...
                pass
        except Exception as e:
            print(f"Simplification error: {e}")
            await websocket.send_json({
                "type": "error",
                "message": "Failed to simplify medical terms"
            })
        
        # Get questions
        try:
            full_transcript = await db.get_full_transcript(session_id)
            questions = await gemini_service.suggest_questions(full_transcript)
            if questions:
                # Send questions...
                pass
        except Exception as e:
            print(f"Question generation error: {e}")
            # Don't send error to user, just log it
    
    except Exception as e:
        print(f"Transcript handling error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Failed to process transcript"
        })
```

## Database Integration

### Add Helper Method

In `backend/database.py`:

```python
async def get_full_transcript(session_id: str) -> str:
    """Get full transcript for a session."""
    query = """
        SELECT text FROM transcript_chunks
        WHERE session_id = $1
        ORDER BY timestamp ASC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, session_id)
        return " ".join(row["text"] for row in rows)
```

### Store AI-Generated Content

Ensure database methods exist:

```python
async def add_simplification(session_id: str, term: str, explanation: str):
    """Store a medical term simplification."""
    query = """
        INSERT INTO simplifications (session_id, term, explanation)
        VALUES ($1, $2, $3)
    """
    
    async with pool.acquire() as conn:
        await conn.execute(query, session_id, term, explanation)


async def save_summary(session_id: str, summary: Dict):
    """Store visit summary."""
    query = """
        INSERT INTO summaries (
            session_id, title, diagnosis, medications,
            instructions, follow_up, key_points
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """
    
    async with pool.acquire() as conn:
        await conn.execute(
            query,
            session_id,
            summary["title"],
            summary["diagnosis"],
            json.dumps(summary["medications"]),
            json.dumps(summary["instructions"]),
            summary["follow_up"],
            json.dumps(summary["key_points"])
        )
```

## Testing Integration

### Unit Tests

Test AI service integration:

```python
# backend/tests/test_ai_integration.py

import pytest
from unittest.mock import Mock, patch
from main import handle_transcript, handle_end_session

@pytest.mark.asyncio
async def test_handle_transcript_with_medical_terms():
    """Test transcript handling with medical terms."""
    websocket = Mock()
    session_id = "test-session"
    data = {
        "type": "transcript",
        "text": "Patient has hypertension",
        "language": "en"
    }
    
    with patch('main.gemini_service.simplify_terms') as mock_simplify:
        mock_simplify.return_value = [
            {"term": "hypertension", "explanation": "high blood pressure"}
        ]
        
        await handle_transcript(websocket, session_id, data)
        
        # Verify simplification sent
        websocket.send_json.assert_called()


@pytest.mark.asyncio
async def test_handle_end_session_generates_summary():
    """Test session end generates summary."""
    websocket = Mock()
    session_id = "test-session"
    
    with patch('main.gemini_service.generate_summary') as mock_summary:
        mock_summary.return_value = {
            "title": "Test Visit",
            "diagnosis": "Test",
            "medications": [],
            "instructions": [],
            "follow_up": "",
            "key_points": []
        }
        
        await handle_end_session(websocket, session_id)
        
        # Verify summary sent
        websocket.send_json.assert_called()
```

### Integration Tests

Test full workflow:

```python
@pytest.mark.asyncio
async def test_full_session_workflow():
    """Test complete session workflow with AI."""
    # Connect WebSocket
    async with websocket_connect("ws://localhost:8000/ws/session") as ws:
        # Send transcript
        await ws.send_json({
            "type": "transcript",
            "text": "Patient has hypertension and tachycardia"
        })
        
        # Receive simplification
        response = await ws.receive_json()
        assert response["type"] == "simplification"
        assert len(response["terms"]) > 0
        
        # Receive questions
        response = await ws.receive_json()
        assert response["type"] == "questions"
        assert len(response["suggestions"]) >= 2
        
        # End session
        await ws.send_json({"type": "end_session"})
        
        # Receive summary
        response = await ws.receive_json()
        assert response["type"] == "summary"
        assert "title" in response["data"]
```

## Deployment

### Environment Variables

Ensure these are set in production:

```bash
GEMINI_API_KEY=your_production_api_key
LOG_LEVEL=INFO
```

### Performance Monitoring

Add monitoring in production:

```python
from gemini_service import GeminiService

# Initialize service
gemini_service = GeminiService(api_key=api_key)

# Periodic stats logging
@app.on_event("startup")
async def startup_event():
    async def log_stats():
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            stats = gemini_service.get_performance_stats()
            print(f"AI Performance: {stats}")
    
    asyncio.create_task(log_stats())
```

### Rate Limiting

The service handles rate limiting automatically, but monitor usage:

```python
stats = gemini_service.get_performance_stats()
if stats["total_requests"] > 1000:
    print("Warning: High API usage")
```

### Error Monitoring

Log all AI errors:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_service.log'),
        logging.StreamHandler()
    ]
)
```

## Troubleshooting

### Issue: API Key Not Found

**Error**: `ValueError: GEMINI_API_KEY is required`

**Solution**:
```bash
# Check environment variable
echo $GEMINI_API_KEY

# Set if missing
export GEMINI_API_KEY=your_api_key
```

### Issue: Rate Limit Exceeded

**Error**: Requests queuing for long time

**Solution**:
- Check `get_performance_stats()` for request count
- Consider upgrading Gemini API tier
- Implement request batching

### Issue: Slow Response Times

**Error**: Requests taking > 5 seconds

**Solution**:
```python
stats = gemini_service.get_performance_stats()
print(f"Slow requests: {stats['slow_request_percentage']}%")

# If high, check:
# 1. Network latency
# 2. Transcript length
# 3. API status
```

### Issue: JSON Parsing Errors

**Error**: `ValueError: Failed to parse JSON response`

**Solution**:
- Check prompt templates in `prompts.py`
- Verify Gemini model version
- Add more explicit JSON format examples

## Best Practices

### 1. Async/Await

Always use async/await for AI calls:

```python
# Good
terms = await gemini_service.simplify_terms(transcript)

# Bad (will block)
terms = gemini_service.simplify_terms(transcript)
```

### 2. Error Handling

Handle errors gracefully:

```python
try:
    terms = await gemini_service.simplify_terms(transcript)
except Exception as e:
    logger.error(f"Simplification failed: {e}")
    terms = []  # Use safe default
```

### 3. Context Management

Ensure sufficient context for questions:

```python
full_transcript = await db.get_full_transcript(session_id)
if len(full_transcript.split()) >= 50:
    questions = await gemini_service.suggest_questions(full_transcript)
```

### 4. Performance Monitoring

Monitor regularly:

```python
# Log stats periodically
stats = gemini_service.get_performance_stats()
logger.info(f"AI Stats: {stats}")
```

### 5. Testing

Test AI integration thoroughly:

```python
# Test with real medical conversations
# Test error scenarios
# Test rate limiting
# Test performance under load
```

## Complete Integration Example

```python
# backend/main.py

import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from gemini_service import GeminiService
from database import DatabaseService

app = FastAPI()

# Initialize services
gemini_service = GeminiService(api_key=os.getenv("GEMINI_API_KEY"))
db = DatabaseService(connection_string=os.getenv("DATABASE_URL"))

@app.on_event("startup")
async def startup():
    await db.init_db()

@app.websocket("/ws/session")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = await db.create_session()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "transcript":
                # Process transcript
                transcript = data["text"]
                await db.add_transcript_chunk(session_id, transcript)
                
                # Simplify terms
                terms = await gemini_service.simplify_terms(transcript)
                if terms:
                    for term in terms:
                        await db.add_simplification(
                            session_id, term["term"], term["explanation"]
                        )
                    await websocket.send_json({
                        "type": "simplification",
                        "terms": terms
                    })
                
                # Generate questions
                full_transcript = await db.get_full_transcript(session_id)
                questions = await gemini_service.suggest_questions(full_transcript)
                if questions:
                    await websocket.send_json({
                        "type": "questions",
                        "suggestions": questions
                    })
            
            elif data["type"] == "end_session":
                # Generate summary
                full_transcript = await db.get_full_transcript(session_id)
                summary = await gemini_service.generate_summary(full_transcript)
                await db.save_summary(session_id, summary)
                await websocket.send_json({
                    "type": "summary",
                    "data": summary
                })
                break
    
    except WebSocketDisconnect:
        await db.end_session(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Next Steps

1. Copy files to backend
2. Update environment variables
3. Integrate with WebSocket handlers
4. Test integration
5. Deploy to production
6. Monitor performance

For questions or issues, refer to the API documentation or open an issue.
