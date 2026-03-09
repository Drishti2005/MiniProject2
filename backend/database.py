# TEAM: Backend Infrastructure
# Database service for Supabase PostgreSQL operations
# Handles all database interactions for sessions, transcripts, simplifications, and summaries

import asyncpg
from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing database operations with Supabase PostgreSQL"""

    def __init__(self, connection_string: str):
        """
        Initialize database service with connection string

        Args:
            connection_string: PostgreSQL connection string from Supabase
        """
        self.connection_string = connection_string
        self.pool = None

    async def init_db(self):
        """
        Initialize database connection pool and create tables if they don't exist

        Creates tables:
        - sessions: Medical appointment sessions
        - transcript_chunks: Speech transcript segments
        - simplifications: Medical term explanations
        - summaries: Visit summaries
        """
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=5,
                max_size=10,
                command_timeout=5
            )
            
            logger.info("Database connection pool created")
            
            # Create tables if they don't exist
            async with self.pool.acquire() as conn:
                # Sessions table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title TEXT,
                        language TEXT DEFAULT 'en',
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        ended_at TIMESTAMPTZ
                    )
                """)
                
                # Create index on created_at for performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_created_at 
                    ON sessions(created_at DESC)
                """)
                
                # Transcript chunks table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS transcript_chunks (
                        id SERIAL PRIMARY KEY,
                        session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
                        text TEXT NOT NULL,
                        timestamp TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                
                # Create index on session_id and timestamp
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transcript_session 
                    ON transcript_chunks(session_id, timestamp)
                """)
                
                # Simplifications table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS simplifications (
                        id SERIAL PRIMARY KEY,
                        session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
                        term TEXT NOT NULL,
                        explanation TEXT NOT NULL,
                        timestamp TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                
                # Create index on session_id and timestamp
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_simplifications_session 
                    ON simplifications(session_id, timestamp)
                """)
                
                # Summaries table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS summaries (
                        id SERIAL PRIMARY KEY,
                        session_id UUID REFERENCES sessions(id) ON DELETE CASCADE UNIQUE,
                        title TEXT,
                        diagnosis TEXT,
                        medications JSONB,
                        instructions JSONB,
                        follow_up TEXT,
                        key_points JSONB,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                
                # Create index on session_id
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_summaries_session 
                    ON summaries(session_id)
                """)
                
                logger.info("Database schema initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def create_session(self, language: str = "en") -> str:
        """
        Create a new session in the database

        Args:
            language: User's preferred language (default: "en")

        Returns:
            session_id: UUID of the created session
        """
        try:
            async with self.pool.acquire() as conn:
                session_id = await conn.fetchval(
                    """
                    INSERT INTO sessions (language, title) 
                    VALUES ($1, $2) 
                    RETURNING id
                    """,
                    language,
                    f"Medical Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                logger.info(f"Created session: {session_id}")
                return str(session_id)
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    async def end_session(self, session_id: str):
        """
        Mark a session as ended by updating the ended_at timestamp

        Args:
            session_id: UUID of the session to end
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE sessions 
                    SET ended_at = NOW() 
                    WHERE id = $1
                    """,
                    session_id
                )
                logger.info(f"Ended session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise

    async def add_transcript_chunk(self, session_id: str, text: str):
        """
        Store a transcript chunk in the database

        Args:
            session_id: UUID of the session
            text: Transcript text
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO transcript_chunks (session_id, text) 
                    VALUES ($1, $2)
                    """,
                    session_id,
                    text
                )
                logger.debug(f"Added transcript chunk to session {session_id}")
        except Exception as e:
            logger.error(f"Failed to add transcript chunk: {e}")
            raise

    async def add_simplification(self, session_id: str, term: str, explanation: str):
        """
        Store a medical term simplification in the database

        Args:
            session_id: UUID of the session
            term: Medical term
            explanation: Plain-language explanation
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO simplifications (session_id, term, explanation) 
                    VALUES ($1, $2, $3)
                    """,
                    session_id,
                    term,
                    explanation
                )
                logger.debug(f"Added simplification to session {session_id}: {term}")
        except Exception as e:
            logger.error(f"Failed to add simplification: {e}")
            raise

    async def save_summary(self, session_id: str, summary: Dict):
        """
        Store a visit summary in the database

        Args:
            session_id: UUID of the session
            summary: Dictionary with summary fields (title, diagnosis, medications, etc.)
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO summaries 
                    (session_id, title, diagnosis, medications, instructions, follow_up, key_points) 
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (session_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        diagnosis = EXCLUDED.diagnosis,
                        medications = EXCLUDED.medications,
                        instructions = EXCLUDED.instructions,
                        follow_up = EXCLUDED.follow_up,
                        key_points = EXCLUDED.key_points
                    """,
                    session_id,
                    summary.get("title", ""),
                    summary.get("diagnosis", ""),
                    json.dumps(summary.get("medications", [])),
                    json.dumps(summary.get("instructions", [])),
                    summary.get("follow_up", ""),
                    json.dumps(summary.get("key_points", []))
                )
                logger.info(f"Saved summary for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            raise

    async def get_all_sessions(self) -> List[Dict]:
        """
        Retrieve all sessions ordered by created_at descending

        Returns:
            List of session dictionaries with basic info
        """
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, title, language, created_at, ended_at 
                    FROM sessions 
                    ORDER BY created_at DESC
                    """
                )
                
                sessions = []
                for row in rows:
                    sessions.append({
                        "id": str(row["id"]),
                        "title": row["title"],
                        "language": row["language"],
                        "created_at": row["created_at"].isoformat(),
                        "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None
                    })
                
                return sessions
        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            raise

    async def get_session_details(self, session_id: str) -> Dict:
        """
        Retrieve complete session data including transcript, simplifications, and summary

        Args:
            session_id: UUID of the session

        Returns:
            Dictionary with session, transcript, simplifications, and summary
        """
        try:
            async with self.pool.acquire() as conn:
                # Get session
                session_row = await conn.fetchrow(
                    """
                    SELECT id, title, language, created_at, ended_at 
                    FROM sessions 
                    WHERE id = $1
                    """,
                    session_id
                )
                
                if not session_row:
                    return None
                
                # Get transcript chunks
                transcript_rows = await conn.fetch(
                    """
                    SELECT id, session_id, text, timestamp 
                    FROM transcript_chunks 
                    WHERE session_id = $1 
                    ORDER BY timestamp ASC
                    """,
                    session_id
                )
                
                # Get simplifications
                simplification_rows = await conn.fetch(
                    """
                    SELECT id, session_id, term, explanation, timestamp 
                    FROM simplifications 
                    WHERE session_id = $1 
                    ORDER BY timestamp ASC
                    """,
                    session_id
                )
                
                # Get summary
                summary_row = await conn.fetchrow(
                    """
                    SELECT id, session_id, title, diagnosis, medications, 
                           instructions, follow_up, key_points, created_at 
                    FROM summaries 
                    WHERE session_id = $1
                    """,
                    session_id
                )
                
                # Build response
                result = {
                    "session": {
                        "id": str(session_row["id"]),
                        "title": session_row["title"],
                        "language": session_row["language"],
                        "created_at": session_row["created_at"].isoformat(),
                        "ended_at": session_row["ended_at"].isoformat() if session_row["ended_at"] else None
                    },
                    "transcript": [
                        {
                            "id": row["id"],
                            "session_id": str(row["session_id"]),
                            "text": row["text"],
                            "timestamp": row["timestamp"].isoformat()
                        }
                        for row in transcript_rows
                    ],
                    "simplifications": [
                        {
                            "id": row["id"],
                            "session_id": str(row["session_id"]),
                            "term": row["term"],
                            "explanation": row["explanation"],
                            "timestamp": row["timestamp"].isoformat()
                        }
                        for row in simplification_rows
                    ],
                    "summary": None
                }
                
                if summary_row:
                    result["summary"] = {
                        "id": summary_row["id"],
                        "session_id": str(summary_row["session_id"]),
                        "title": summary_row["title"],
                        "diagnosis": summary_row["diagnosis"],
                        "medications": json.loads(summary_row["medications"]) if summary_row["medications"] else [],
                        "instructions": json.loads(summary_row["instructions"]) if summary_row["instructions"] else [],
                        "follow_up": summary_row["follow_up"],
                        "key_points": json.loads(summary_row["key_points"]) if summary_row["key_points"] else [],
                        "created_at": summary_row["created_at"].isoformat()
                    }
                
                return result
                
        except Exception as e:
            logger.error(f"Failed to get session details for {session_id}: {e}")
            raise

    async def delete_session(self, session_id: str):
        """
        Delete a session and all related data (cascade delete)

        Args:
            session_id: UUID of the session to delete
        """
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    DELETE FROM sessions WHERE id = $1
                    """,
                    session_id
                )
                logger.info(f"Deleted session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise
    
    async def get_simplification_count(self, session_id: str) -> int:
        """
        Get count of simplifications for a session (used in property tests)

        Args:
            session_id: UUID of the session

        Returns:
            Count of simplifications
        """
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM simplifications WHERE session_id = $1
                    """,
                    session_id
                )
                return count
        except Exception as e:
            logger.error(f"Failed to get simplification count: {e}")
            raise
