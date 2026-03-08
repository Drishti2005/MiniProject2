# Project Folder Structure - Team Responsibilities

## Complete Project Structure

```
sidekick-medical-assistant/
├── .env                                    # [Backend Infrastructure] Environment variables
├── .env.example                            # [Backend Infrastructure] Example environment config
├── README.md                               # [All Teams] Project documentation
│
├── .kiro/                                  # Kiro spec files (reference only)
│   └── specs/
│       └── sidekick-medical-assistant/
│           ├── requirements.md
│           ├── design.md
│           ├── tasks.md
│           ├── tasks-backend-infrastructure.md
│           ├── tasks-ai-integration.md
│           ├── tasks-frontend.md
│           └── FOLDER_STRUCTURE.md (this file)
│
├── backend/                                # Backend code
│   ├── main.py                            # [Backend Infrastructure] FastAPI app, routes, WebSocket
│   ├── database.py                        # [Backend Infrastructure] Supabase PostgreSQL service
│   ├── gemini_service.py                  # [AI Integration] Gemini API integration
│   ├── models.py                          # [Backend Infrastructure] Pydantic models
│   ├── requirements.txt                   # [Backend Infrastructure] Python dependencies
│   │
│   └── tests/                             # Backend tests
│       ├── test_database.py              # [Backend Infrastructure] Database tests
│       ├── test_websocket.py             # [Backend Infrastructure] WebSocket tests
│       ├── test_rest_api.py              # [Backend Infrastructure] REST API tests
│       ├── test_gemini_service.py        # [AI Integration] Gemini service tests
│       ├── test_simplification.py        # [AI Integration] Medical term tests
│       ├── test_questions.py             # [AI Integration] Question generation tests
│       ├── test_translation.py           # [AI Integration] Translation tests
│       └── test_summary.py               # [AI Integration] Summary generation tests
│
└── frontend/                              # Frontend code
    ├── index.html                         # [Frontend] Main application page
    ├── history.html                       # [Frontend] Session history page
    │
    ├── css/
    │   └── style.css                      # [Frontend] All application styles
    │
    ├── js/
    │   ├── app.js                         # [Frontend] WebSocket client, session lifecycle
    │   ├── speech.js                      # [Frontend] Web Speech API wrapper
    │   ├── ui.js                          # [Frontend] DOM manipulation, UI updates
    │   └── history.js                     # [Frontend] History page logic
    │
    └── tests/                             # Frontend tests
        ├── test_speech.js                 # [Frontend] Speech recognition tests
        ├── test_websocket.js              # [Frontend] WebSocket client tests
        ├── test_ui.js                     # [Frontend] UI manager tests
        └── test_history.js                # [Frontend] History page tests
```

---

## Team 1: Backend Infrastructure

### Responsibilities
- Database services and schema
- WebSocket communication
- REST API endpoints
- Core server setup
- Backend error handling
- Backend security

### Files to Create/Modify

#### Configuration Files
```
.env.example                               # Environment variable template
README.md (backend section)                # Backend setup documentation
```

#### Backend Core Files
```
backend/main.py                            # FastAPI application
  - FastAPI app setup with CORS
  - Static file serving
  - REST API endpoints (GET /, GET /api/sessions, GET /api/sessions/{id}, DELETE /api/sessions/{id})
  - WebSocket endpoint (ws://localhost:8000/ws/session)
  - WebSocket message handlers (handle_transcript, handle_end_session)
  - Startup event for database initialization
  - Error handling and logging

backend/database.py                        # Database service
  - DatabaseService class
  - Connection pooling with asyncpg
  - init_db() - Create Supabase PostgreSQL tables
  - create_session(language) - Create new session
  - end_session(session_id) - Update ended_at timestamp
  - get_all_sessions() - Retrieve session list
  - get_session_details(session_id) - Retrieve full session data
  - delete_session(session_id) - Cascade delete
  - add_transcript_chunk(session_id, text) - Store transcript
  - add_simplification(session_id, term, explanation) - Store simplification
  - save_summary(session_id, summary) - Store visit summary

backend/models.py                          # Pydantic models
  - TranscriptMessage
  - SimplificationMessage, SimplificationTerm
  - QuestionsMessage
  - TranslationMessage
  - SummaryMessage, SummaryData
  - ErrorMessage
  - Session, TranscriptChunk, Simplification, Summary
  - SessionDetail

backend/requirements.txt                   # Python dependencies
  - fastapi
  - uvicorn[standard]
  - websockets
  - asyncpg
  - google-generativeai
  - python-dotenv
  - aiosqlite (for local testing)
```

#### Backend Tests
```
backend/tests/test_database.py             # Database service tests
  - Test session creation
  - Test session management (CRUD)
  - Test data persistence
  - Test cascade delete
  - Property tests for session creation, simplification accumulation, deletion cascade

backend/tests/test_websocket.py            # WebSocket tests
  - Test connection lifecycle
  - Test message handling
  - Test message validation
  - Test message order preservation
  - Property tests for WebSocket functionality

backend/tests/test_rest_api.py             # REST API tests
  - Test GET /api/sessions
  - Test GET /api/sessions/{id}
  - Test DELETE /api/sessions/{id}
  - Test HTTP status codes
  - Test error responses
```

---

## Team 2: AI Integration

### Responsibilities
- Google Gemini API integration
- Medical terminology simplification
- Question suggestion engine
- Translation services
- Visit summary generation
- AI error handling
- Prompt engineering

### Files to Create/Modify

#### AI Service Files
```
backend/gemini_service.py                  # Gemini API service
  - GeminiService class
  - __init__(api_key) - Initialize Gemini client
  - Rate limiting (15 requests per minute) with request queue
  - Timeout handling (10 seconds per request)
  - Retry logic with exponential backoff (3 attempts)
  
  Methods:
  - simplify_terms(transcript) -> List[Dict]
    * Medical term simplification prompt
    * Parse JSON response
    * Return term-explanation pairs
  
  - suggest_questions(full_transcript) -> List[str]
    * Question generation prompt
    * Parse JSON response
    * Return 2-3 questions
  
  - generate_summary(full_transcript) -> Dict
    * Visit summary prompt
    * Parse JSON response
    * Extract all fields (title, diagnosis, medications, instructions, follow_up, key_points)
  
  - translate_text(text, target_language) -> str
    * Translation prompt
    * Support languages: Spanish, Hindi, Mandarin, French, Arabic
    * Return translated text
  
  Error Handling:
  - Handle timeout errors
  - Handle rate limit errors
  - Handle API errors with user-friendly messages
  - Parse and validate JSON responses
  - Comprehensive error logging

README.md (AI section)                     # AI service documentation
  - Gemini API setup
  - Prompt templates
  - Rate limiting behavior
  - Error handling
```

#### AI Tests
```
backend/tests/test_gemini_service.py       # Gemini service tests
  - Test API initialization
  - Test rate limiting
  - Test timeout handling
  - Test retry logic
  - Test error handling
  - Property tests for rate limiting, response parsing, error handling

backend/tests/test_simplification.py       # Medical term simplification tests
  - Test with medical terms
  - Test with no medical terms
  - Test with multiple terms
  - Test prompt formatting
  - Property tests for simplification generation, response time

backend/tests/test_questions.py            # Question generation tests
  - Test with sufficient context
  - Test with minimal context
  - Test with changing topics
  - Test prompt formatting
  - Property tests for question cardinality, transmission time

backend/tests/test_translation.py          # Translation tests
  - Test translation to each supported language
  - Test with medical terminology
  - Test with simple explanations
  - Test prompt formatting
  - Property tests for translation transmission

backend/tests/test_summary.py              # Summary generation tests
  - Test with complete conversation
  - Test with short conversation
  - Test JSON parsing and field extraction
  - Test prompt formatting
  - Property tests for summary structure, generation time
```

---

## Team 3: Frontend

### Responsibilities
- Speech recognition (Web Speech API)
- WebSocket client
- UI components and styling
- Session history
- User interface design
- Frontend error handling
- Accessibility

### Files to Create/Modify

#### HTML Files
```
frontend/index.html                        # Main application page
  Structure:
  - Header with app title and History link
  - Three-panel layout:
    * Live Transcript panel (left)
    * Simplified Terms panel (right top)
    * Suggested Questions panel (right bottom)
  - Recording controls (Start/Stop buttons)
  - Language selection dropdown
  - Translation panel (initially hidden)
  - Summary modal/view
  - Script tags for speech.js, app.js, ui.js
  - Link to style.css

frontend/history.html                      # Session history page
  Structure:
  - Header with app title and back link
  - Session list container
  - Session detail view
  - Delete confirmation modal
  - Script tag for history.js
  - Link to style.css
```

#### CSS Files
```
frontend/css/style.css                     # All application styles
  Styles:
  - Medical-themed color scheme (blues, whites, high contrast)
  - Three-panel layout with flexbox/grid
  - Recording indicator (pulsing red dot animation)
  - Simplified terms with term highlighting
  - Suggested questions as numbered list
  - Translation panel styles
  - Summary modal/view styles
  - Responsive layout (min-width 768px for tablet/desktop)
  - Smooth animations for new content
  - Button styles (primary, secondary, danger)
  - Error message styles
  - Loading indicators
  - Accessibility styles (focus indicators, high contrast)
```

#### JavaScript Files
```
frontend/js/speech.js                      # Speech recognition module
  - SpeechRecognitionManager class
  - Browser compatibility check (isSupported)
  - start() - Initialize continuous recognition with interim results
  - stop() - Terminate recognition
  - Error handling with automatic restart (up to 3 attempts)
  - Handle error types: no-speech, network, not-allowed, audio-capture
  - onTranscript(text, isFinal) callback
  - onError(error) callback

frontend/js/app.js                         # WebSocket client and session lifecycle
  - WebSocketClient class
  - Connection establishment (ws://localhost:8000/ws/session)
  - Automatic reconnection with exponential backoff (1s, 2s, 4s)
  - Heartbeat ping every 30 seconds
  - Message queue for offline resilience
  - send(message) - Send JSON messages
  - onMessage(handler) - Route incoming messages by type
  - Handle message types: simplification, questions, translation, summary, error
  - Session lifecycle management
  - Language selection handling
  - Integration with SpeechRecognitionManager and UIManager

frontend/js/ui.js                          # UI manager
  - UIManager class
  - updateTranscript(text, isFinal) - Append transcript with auto-scroll
  - addSimplification(term, explanation) - Display with highlighting
  - updateQuestions(questions) - Replace suggested questions
  - showTranslation(text) - Display translated text
  - displaySummary(summary) - Show structured visit summary
  - setRecordingState(isRecording) - Toggle recording button and indicator
  - showError(message) - Display error notifications
  - clearSession() - Reset UI for new session
  - toggleTranslationPanel(visible) - Show/hide translation panel

frontend/js/history.js                     # History page logic
  - Fetch sessions from GET /api/sessions on page load
  - Render session list with title, date, summary preview
  - Click handler to fetch and display full session details (GET /api/sessions/{id})
  - Delete button handler with confirmation (DELETE /api/sessions/{id})
  - Update UI immediately after deletion
  - Error handling for API calls
```

#### Frontend Tests
```
frontend/tests/test_speech.js              # Speech recognition tests
  - Test browser compatibility detection
  - Test error handling for different error types
  - Test automatic restart logic
  - Property tests for speech recognition activation, transcript transmission, error recovery

frontend/tests/test_websocket.js           # WebSocket client tests
  - Test connection lifecycle
  - Test message routing by type
  - Test reconnection logic
  - Test error handling
  - Property tests for message processing time, reconnection attempts, message type support

frontend/tests/test_ui.js                  # UI manager tests
  - Test transcript appending and scrolling
  - Test simplification display with highlighting
  - Test question replacement (not append)
  - Test recording state visual indicator
  - Test error message display
  - Property tests for simplification display, question updates, summary display, auto-scroll, term highlighting, recording indicator

frontend/tests/test_history.js             # History page tests
  - Test session list rendering
  - Test session detail display
  - Test delete functionality
  - Test UI update after deletion
  - Property tests for session list ordering, session display, session detail completeness, delete button presence, deletion UI update
```

#### Frontend Documentation
```
README.md (frontend section)               # Frontend documentation
  - Browser compatibility (Chrome, Edge required for Web Speech API)
  - Setup instructions
  - Usage instructions
  - Feature documentation
  - Troubleshooting
```

---

## Shared Files (All Teams Contribute)

```
README.md                                  # Complete project documentation
  Sections:
  - [All Teams] Project overview and features
  - [Backend Infrastructure] Backend setup and API documentation
  - [AI Integration] Gemini API setup and configuration
  - [Frontend] Frontend setup and browser requirements
  - [All Teams] Usage instructions
  - [All Teams] Troubleshooting

.env                                       # Environment variables (not committed to git)
  - GEMINI_API_KEY=your_api_key_here
  - SUPABASE_URL=your_supabase_url
  - SUPABASE_KEY=your_supabase_key
  - DATABASE_URL=postgresql://...
```

---

## Integration Points

### Backend Infrastructure ↔ AI Integration
- Backend Infrastructure calls AI Integration's `gemini_service.py` methods
- Shared: `backend/models.py` for data structures

### Backend Infrastructure ↔ Frontend
- WebSocket message formats (defined in `backend/models.py`)
- REST API contracts (defined in `backend/main.py`)
- Frontend calls backend endpoints

### AI Integration ↔ Frontend
- AI responses displayed by Frontend UI
- Frontend sends language preferences that affect AI translation

---

## Development Workflow

### Phase 1: Foundation (Week 1)
1. **Backend Infrastructure**: Set up project structure, database, models
2. **AI Integration**: Set up Gemini service foundation
3. **Frontend**: Set up HTML structure and basic CSS

### Phase 2: Core Features (Week 2)
1. **Backend Infrastructure**: Implement WebSocket and REST API
2. **AI Integration**: Implement simplification and question generation
3. **Frontend**: Implement speech recognition and WebSocket client

### Phase 3: Advanced Features (Week 3)
1. **Backend Infrastructure**: Implement translation backend logic
2. **AI Integration**: Implement translation and summary generation
3. **Frontend**: Implement UI manager and session history

### Phase 4: Polish and Testing (Week 4)
1. **All Teams**: Error handling, performance optimization, security
2. **All Teams**: Comprehensive testing (unit, property, integration)
3. **All Teams**: Documentation and deployment preparation

---

## Git Branch Strategy (Recommended)

```
main                                       # Production-ready code
├── develop                                # Integration branch
│   ├── feature/backend-infrastructure     # Backend Infrastructure team
│   ├── feature/ai-integration             # AI Integration team
│   └── feature/frontend                   # Frontend team
```

Each team works on their feature branch and merges to `develop` at checkpoints. After testing, `develop` merges to `main`.

---

## Notes

- Each team should focus on their assigned files
- Coordinate at integration points (see Integration Points section)
- Use checkpoints in task files to sync progress
- All teams contribute to README.md in their respective sections
- Follow the task files for detailed implementation steps
- Run tests frequently to catch integration issues early
