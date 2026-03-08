# Implementation Plan: Backend Infrastructure Team

## Overview

This task list covers backend infrastructure, database services, WebSocket communication, and REST API endpoints. All tasks are mandatory and build the foundation for the Sidekick AI Medical Appointment Assistant.

## Team Responsibility

Backend Infrastructure - Database, WebSocket, REST API, Core Server Setup

## Tasks

- [ ] 1. Set up project structure and configuration
  - Create directory structure: `backend/`, `frontend/`, `frontend/css/`, `frontend/js/`
  - Create `backend/requirements.txt` with dependencies: fastapi, uvicorn, websockets, asyncpg, google-generativeai, python-dotenv, aiosqlite
  - Create `.env.example` file with required environment variables
  - Create `backend/models.py` with all Pydantic models for WebSocket messages and database entities
  - _Requirements: 15.1, 15.2_

- [ ] 2. Implement database service and schema
  - [ ] 2.1 Create `backend/database.py` with DatabaseService class
    - Implement connection pooling with asyncpg
    - Implement `init_db()` method to create tables if they don't exist
    - Create SQL schema for sessions, transcript_chunks, simplifications, summaries tables with indexes
    - _Requirements: 8.2, 8.8, 15.3_
  
  - [ ] 2.2 Implement session management methods
    - Implement `create_session(language: str) -> str` to create new session
    - Implement `end_session(session_id: str)` to update ended_at timestamp
    - Implement `get_all_sessions() -> List[Dict]` to retrieve session list
    - Implement `get_session_details(session_id: str) -> Dict` to retrieve full session data
    - Implement `delete_session(session_id: str)` with cascade delete
    - _Requirements: 8.3, 8.7, 7.3, 7.7, 7.9_
  
  - [ ] 2.3 Implement data persistence methods
    - Implement `add_transcript_chunk(session_id: str, text: str)` to store transcript
    - Implement `add_simplification(session_id: str, term: str, explanation: str)` to store simplification
    - Implement `save_summary(session_id: str, summary: Dict)` to store visit summary
    - _Requirements: 8.4, 8.5, 8.6_
  
  - [ ] 2.4 Write property test for session creation
    - **Property 15: WebSocket Session Creation**
    - For any WebSocket connection, verify session record is created with unique ID, language, and timestamp
    - **Validates: Requirements 4.2, 8.3**
  
  - [ ] 2.5 Write property test for simplification accumulation
    - **Property 8: Simplification Accumulation Invariant**
    - For any session, verify adding a simplification increases list size by exactly 1
    - **Validates: Requirements 2.6**
  
  - [ ] 2.6 Write property test for session deletion cascade
    - **Property 35: Session Deletion Cascade**
    - For any session deletion, verify all related records are removed from all tables
    - **Validates: Requirements 7.9, 12.7**

- [ ] 3. Checkpoint - Verify database functionality
  - Ensure database service can create sessions and store data
  - Ensure all CRUD operations work correctly
  - Run all database tests and verify they pass
  - Ask the user if questions arise

- [ ] 4. Implement WebSocket handler and REST API
  - [ ] 4.1 Create `backend/main.py` with FastAPI application
    - Set up FastAPI app with CORS middleware
    - Configure static file serving for frontend directory
    - Implement startup event to initialize database
    - Load environment variables and validate configuration
    - _Requirements: 15.4, 15.5_
  
  - [ ] 4.2 Implement REST API endpoints
    - Implement `GET /` to serve `frontend/index.html`
    - Implement `GET /api/sessions` to return all sessions
    - Implement `GET /api/sessions/{id}` to return session details
    - Implement `DELETE /api/sessions/{id}` to delete session
    - Add error handling for 404 Not Found and 500 Internal Server Error
    - _Requirements: 12.1, 12.2, 12.4, 12.6, 12.8, 12.9_
  
  - [ ] 4.3 Implement WebSocket endpoint
    - Implement `ws://localhost:8000/ws/session` endpoint
    - Handle WebSocket connection lifecycle (accept, disconnect)
    - Create session on connection establishment
    - End session on disconnection
    - _Requirements: 4.1, 4.2_
  
  - [ ] 4.4 Implement WebSocket message handlers
    - Implement `handle_transcript()` to process transcript chunks
    - Store transcript chunk in database
    - Call Gemini service for simplification and questions (integrate with AI team's service)
    - Send results back to client via WebSocket
    - Implement `handle_end_session()` to generate visit summary
    - Compile full transcript and call Gemini service
    - Store summary in database and send to client
    - _Requirements: 2.1, 3.2, 5.2, 5.3, 5.5_
  
  - [ ] 4.5 Implement WebSocket error handling
    - Validate incoming message format
    - Handle invalid message types
    - Send error messages to client
    - Log errors with context
    - _Requirements: 11.5, 11.7_
  
  - [ ] 4.6 Write property test for WebSocket message validation
    - **Property 51: WebSocket Message Validation**
    - For any message received, verify format validation and rejection of invalid messages
    - **Validates: Requirements 11.5**
  
  - [ ] 4.7 Write property test for message order preservation
    - **Property 59: Message Order Preservation**
    - For any sequence of transcript chunks sent rapidly, verify processing in order without drops
    - **Validates: Requirements 13.5**
  
  - [ ] 4.8 Write unit tests for REST API endpoints
    - Test GET /api/sessions returns correct format
    - Test GET /api/sessions/{id} with valid and invalid IDs
    - Test DELETE /api/sessions/{id} cascade behavior
    - Test HTTP status codes (200, 404, 500)
    - _Requirements: 12.3, 12.5, 12.7, 12.9_

- [ ] 5. Checkpoint - Verify backend communication
  - Ensure WebSocket connection establishes successfully
  - Ensure REST API endpoints return correct responses
  - Ensure message routing works correctly
  - Run all backend tests and verify they pass
  - Ask the user if questions arise

- [ ] 6. Implement translation feature backend logic
  - [ ] 6.1 Add translation logic in backend WebSocket handler
    - Check if non-English language is selected
    - Call Gemini service to translate simplifications (integrate with AI team's service)
    - Send translated text to frontend via WebSocket
    - _Requirements: 6.3, 6.4_
  
  - [ ] 6.2 Implement language change re-translation
    - When language changes mid-session, retrieve all existing simplifications
    - Translate each simplification to new language
    - Send all translations to frontend
    - _Requirements: 6.7_
  
  - [ ] 6.3 Write property test for translation request trigger
    - **Property 27: Translation Request Trigger**
    - For any simplification with non-English language selected, verify translation is requested
    - **Validates: Requirements 6.3**
  
  - [ ] 6.4 Write unit tests for translation feature
    - Test language selection storage
    - Test translation request for non-English languages
    - Test language change re-translation
    - _Requirements: 6.2, 6.3, 6.7_

- [ ] 7. Implement visit summary generation backend
  - [ ] 7.1 Enhance backend summary generation
    - Compile all transcript chunks in order
    - Send to Gemini with structured summary prompt (integrate with AI team's service)
    - Parse JSON response and extract all fields: title, diagnosis, medications, instructions, follow_up, key_points
    - Store summary in database
    - Send summary to frontend via WebSocket
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_
  
  - [ ] 7.2 Write property test for summary structure completeness
    - **Property 21: Summary Structure Completeness**
    - For any visit summary, verify all required fields are present
    - **Validates: Requirements 5.4**
  
  - [ ] 7.3 Write property test for summary generation time
    - **Property 25: Summary Generation Time**
    - For any session end, verify summary is generated within 10 seconds
    - **Validates: Requirements 5.8**
  
  - [ ] 7.4 Write unit tests for summary generation
    - Test transcript compilation
    - Test JSON parsing and field extraction
    - Test database storage
    - Test WebSocket transmission
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 8. Checkpoint - Verify complete backend feature set
  - Test complete backend lifecycle: receive transcript, store data, call AI services, return results
  - Test session history endpoints
  - Test error handling: database errors, API errors
  - Run all backend tests and verify they pass
  - Ask the user if questions arise

- [ ] 9. Implement comprehensive backend error handling
  - [ ] 9.1 Add backend error handling
    - Implement database error handling with appropriate HTTP status codes
    - Implement Gemini API error handling with retry logic (coordinate with AI team)
    - Implement WebSocket error handling with error messages to client
    - Implement comprehensive error logging with timestamps and context
    - _Requirements: 11.3, 11.4, 11.5, 11.6, 11.7_
  
  - [ ] 9.2 Write property tests for backend error handling
    - **Property 50: Database Error Response** - For any database failure, verify 503 response
    - **Validates: Requirements 11.4**
  
  - [ ] 9.3 Write unit tests for error scenarios
    - Test WebSocket connection failure
    - Test database connection failure
    - Test invalid WebSocket message format
    - _Requirements: 11.2, 11.4, 11.5_

- [ ] 10. Implement performance optimizations
  - [ ] 10.1 Add performance monitoring
    - Add timing logs for transcript processing
    - Add timing logs for database queries
    - _Requirements: 13.1, 13.3_
  
  - [ ] 10.2 Optimize database queries
    - Add indexes on frequently queried columns
    - Use connection pooling efficiently
    - Implement query result caching where appropriate
    - _Requirements: 8.8, 13.3_
  
  - [ ] 10.3 Write property tests for performance constraints
    - **Property 56: Transcript Processing Time** - For any transcript chunk, verify processing within 2 seconds
    - **Property 58: Database Query Performance** - For any simple query, verify completion within 500ms
    - **Validates: Requirements 13.1, 13.3**

- [ ] 11. Add backend security features
  - [ ] 11.1 Implement data sanitization
    - Ensure no audio data is stored, only text transcripts
    - Sanitize logs to remove sensitive medical information
    - Implement secure environment variable loading
    - _Requirements: 14.1, 14.2, 14.5_
  
  - [ ] 11.2 Implement secure communication
    - Use HTTPS for Gemini API calls (coordinate with AI team)
    - Configure WSS for production WebSocket connections
    - Validate all input data
    - _Requirements: 14.3, 14.4_
  
  - [ ] 11.3 Write property tests for security
    - **Property 60: No Audio Storage** - For any session, verify no audio files exist
    - **Property 62: Sensitive Data Sanitization** - For any log entry, verify no sensitive data
    - **Validates: Requirements 14.1, 14.5**
  
  - [ ] 11.4 Write unit tests for security features
    - Test environment variable loading
    - Test log sanitization
    - Test input validation
    - _Requirements: 14.2, 14.5_

- [ ] 12. Create backend documentation and deployment files
  - [ ] 12.1 Create README.md backend section
    - Add backend setup instructions (dependencies, environment variables, database)
    - Add API documentation for REST endpoints and WebSocket messages
    - Add troubleshooting section
    - _Requirements: 15.6_
  
  - [ ] 12.2 Create .env.example
    - List all required environment variables
    - Provide example values and descriptions
    - _Requirements: 15.2_
  
  - [ ] 12.3 Add deployment configuration
    - Document uvicorn configuration options
    - Document Supabase setup for production
    - Add deployment instructions for Render/Railway
    - _Requirements: 15.4, 15.7, 15.8_

- [ ] 13. Final backend integration testing
  - [ ] 13.1 Run complete backend test suite
    - Test all REST endpoints
    - Test WebSocket communication
    - Test database operations
    - Test error scenarios and recovery
    - Verify all property-based tests pass with 100 iterations
    - _Requirements: All backend requirements_
  
  - [ ] 13.2 Final backend code review and cleanup
    - Remove debug logging
    - Remove unused code
    - Ensure consistent code style
    - Verify all comments are accurate
    - Update documentation if needed

- [ ] 14. Final checkpoint - Backend production readiness
  - Verify all backend tests pass (unit, property, integration)
  - Verify all backend requirements are implemented
  - Verify backend documentation is complete and accurate
  - Verify backend works with AI services and frontend
  - Ask the user if ready for deployment

## Notes

- All tasks are mandatory for comprehensive backend implementation
- Coordinate with AI Integration team for Gemini service calls
- Coordinate with Frontend team for WebSocket message formats
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout development
- Property tests validate universal correctness properties with 100 iterations each
- Unit tests validate specific examples and edge cases
