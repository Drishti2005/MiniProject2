# Sidekick Medical Assistant - Backend

Real-time AI-powered medical appointment assistant backend built with FastAPI, WebSocket, and Google Gemini AI.

## Overview

The backend provides:
- **WebSocket endpoint** for real-time bidirectional communication
- **REST API** for session management and history
- **Database service** for PostgreSQL (Supabase) data persistence
- **AI integration** with Google Gemini for medical term simplification, question suggestions, and visit summaries

## Prerequisites

- Python 3.9 or higher
- PostgreSQL database (Supabase recommended)
- Google Gemini API key
- pip or uv for package management

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (not in backend folder):

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
DATABASE_URL=postgresql://user:password@host:port/database
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

**Getting API Keys:**
- **Gemini API**: Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Supabase Database**: Create a free project at [Supabase](https://supabase.com) and copy the connection string from Project Settings > Database

### 3. Initialize Database

The database schema is automatically created on first startup. Tables created:
- `sessions` - Medical appointment sessions
- `transcript_chunks` - Speech transcript segments
- `simplifications` - Medical term explanations
- `summaries` - Visit summaries

### 4. Run the Server

```bash
# From project root
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## API Documentation

### REST Endpoints

#### GET /
Serves the frontend application HTML page.

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Sidekick Medical Assistant",
  "version": "1.0.0"
}
```

#### GET /api/sessions
Returns list of all medical appointment sessions.

**Response:**
```json
{
  "sessions": [
    {
      "id": "uuid",
      "title": "Medical Session 2024-01-15 10:30",
      "language": "en",
      "created_at": "2024-01-15T10:30:00Z",
      "ended_at": "2024-01-15T10:45:00Z"
    }
  ]
}
```

#### GET /api/sessions/{session_id}
Returns complete session details including transcript, simplifications, and summary.

**Response:**
```json
{
  "session": {
    "id": "uuid",
    "title": "Medical Session 2024-01-15 10:30",
    "language": "en",
    "created_at": "2024-01-15T10:30:00Z",
    "ended_at": "2024-01-15T10:45:00Z"
  },
  "transcript": [
    {
      "id": 1,
      "session_id": "uuid",
      "text": "Doctor: Your blood pressure is elevated.",
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ],
  "simplifications": [
    {
      "id": 1,
      "session_id": "uuid",
      "term": "hypertension",
      "explanation": "high blood pressure",
      "timestamp": "2024-01-15T10:30:06Z"
    }
  ],
  "summary": {
    "id": 1,
    "session_id": "uuid",
    "title": "Hypertension Follow-up",
    "diagnosis": "Elevated blood pressure",
    "medications": ["ACE inhibitor"],
    "instructions": ["Take medication daily", "Monitor blood pressure"],
    "follow_up": "Return in 2 weeks",
    "key_points": ["Blood pressure elevated", "Starting new medication"],
    "created_at": "2024-01-15T10:45:00Z"
  }
}
```

#### DELETE /api/sessions/{session_id}
Deletes a session and all related data (cascade delete).

**Response:**
```json
{
  "status": "deleted",
  "session_id": "uuid"
}
```

### WebSocket Endpoint

#### ws://localhost:8000/ws/session

Establishes a bidirectional WebSocket connection for real-time communication.

**Client → Server Messages:**

```javascript
// Send transcript chunk
{
  "type": "transcript",
  "text": "Doctor: Your blood pressure is elevated.",
  "language": "en"
}

// End session and request summary
{
  "type": "end_session"
}
```

**Server → Client Messages:**

```javascript
// Session created confirmation
{
  "type": "session_created",
  "session_id": "uuid"
}

// Medical term simplifications
{
  "type": "simplification",
  "terms": [
    {
      "term": "hypertension",
      "explanation": "high blood pressure"
    }
  ]
}

// Question suggestions
{
  "type": "questions",
  "suggestions": [
    "What are the side effects of this medication?",
    "How often should I check my blood pressure?",
    "When should I schedule a follow-up?"
  ]
}

// Translation (if non-English language selected)
{
  "type": "translation",
  "text": "presión arterial alta",
  "original_term": "hypertension"
}

// Visit summary
{
  "type": "summary",
  "data": {
    "title": "Hypertension Follow-up",
    "diagnosis": "Elevated blood pressure",
    "medications": ["ACE inhibitor"],
    "instructions": ["Take medication daily"],
    "follow_up": "Return in 2 weeks",
    "key_points": ["Blood pressure elevated"]
  }
}

// Error message
{
  "type": "error",
  "message": "Failed to process transcript"
}
```

## Testing

### Run All Tests

```bash
cd backend
pytest
```

### Run Specific Test Categories

```bash
# Property-based tests
pytest tests/test_properties_database.py -v

# API endpoint tests
pytest tests/test_api_endpoints.py -v

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Property-Based Tests

The backend includes comprehensive property-based tests using Hypothesis to verify correctness properties:

- **Property 8**: Simplification Accumulation Invariant
- **Property 9**: Simplification Persistence Completeness
- **Property 21**: Summary Structure Completeness
- **Property 35**: Session Deletion Cascade
- **Property 37**: Transcript Chunk Persistence
- **Property 38**: Session End Timestamp Update

Each property test runs 100 iterations with randomized inputs to ensure universal correctness.

## Architecture

```
backend/
├── main.py              # FastAPI application, WebSocket & REST endpoints
├── database.py          # Database service for PostgreSQL operations
├── models.py            # Pydantic models for data validation
├── requirements.txt     # Python dependencies
├── tests/
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_properties_database.py    # Property-based tests
│   └── test_api_endpoints.py          # REST API unit tests
└── README.md           # This file
```

## Troubleshooting

### Database Connection Errors

**Error:** `asyncpg.exceptions.InvalidCatalogNameError: database "..." does not exist`

**Solution:** Ensure your Supabase database is created and the connection string is correct. Check that you're using the "Connection string" from Supabase (not the "Connection pooling" string).

### Gemini API Errors

**Error:** `google.api_core.exceptions.PermissionDenied: API key not valid`

**Solution:** Verify your GEMINI_API_KEY in the `.env` file. Get a new key from [Google AI Studio](https://makersuite.google.com/app/apikey).

**Error:** `Rate limit exceeded`

**Solution:** The free tier allows 15 requests per minute. The backend implements automatic queuing, but if you're testing heavily, wait a minute before retrying.

### WebSocket Connection Issues

**Error:** WebSocket connection fails or disconnects immediately

**Solution:** 
1. Ensure the backend server is running
2. Check CORS settings if connecting from a different origin
3. Verify no firewall is blocking WebSocket connections
4. Check browser console for detailed error messages

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'ai_service'`

**Solution:** The backend expects the `ai-service` folder to be at the same level as `backend`. Ensure your project structure matches:
```
project/
├── backend/
├── ai-service/
└── frontend/
```

## Performance Considerations

- **Connection Pooling**: Database uses connection pool (5-10 connections) for efficient concurrent access
- **Async Operations**: All I/O operations use async/await for non-blocking execution
- **Rate Limiting**: Gemini API calls are rate-limited to 15 requests/minute (free tier)
- **Indexing**: Database tables have indexes on frequently queried columns

## Security Notes

- **No Audio Storage**: Only text transcripts are stored, never audio recordings
- **Environment Variables**: Sensitive credentials are loaded from `.env` file (never commit this file)
- **HTTPS**: Use HTTPS in production for secure communication
- **WSS**: Use WebSocket Secure (WSS) in production
- **Input Validation**: All WebSocket messages are validated using Pydantic models

## Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production (Render/Railway)

1. Set environment variables in platform dashboard
2. Use production database URL (Supabase)
3. Deploy command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Ensure WSS is enabled for WebSocket connections

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the design document in `.kiro/specs/sidekick-medical-assistant/design.md`
3. Check application logs for detailed error messages
4. Verify all environment variables are set correctly
