# TEAM: Backend Infrastructure
# Database service supporting both PostgreSQL (Supabase) and SQLite
# Handles all database interactions for sessions, transcripts, simplifications, and summaries

import aiosqlite
from typing import List, Dict, Optional
from uuid import uuid4
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing database operations with SQLite"""

    def __init__(self, connection_string: str):
        """
        Initialize database service with connection string

        Args:
            connection_string: SQLite connection string
        """
        import os
        self.connection_string = connection_string
        # Extract database path from SQLite connection string
        self.db_path = connection_string.replace('sqlite+aiosqlite:///', '')
        
        # Ensure directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Created database directory: {db_dir}")
        
        logger.info(f"Using SQLite database: {self.db_path}")

    async def init_db(self):
        """
        Initialize SQLite database and create tables if they don't exist

        Creates tables:
        - sessions: Medical appointment sessions
        - transcript_chunks: Speech transcript segments
        - simplifications: Medical term explanations
        - summaries: Visit summaries
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable foreign keys
                await db.execute("PRAGMA foreign_keys = ON")
                
                # Sessions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        language TEXT DEFAULT 'en',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        ended_at TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_created_at 
                    ON sessions(created_at DESC)
                """)
                
                # Transcript chunks table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS transcript_chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                        text TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_transcript_session 
                    ON transcript_chunks(session_id, timestamp)
                """)
                
                # Simplifications table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS simplifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE,
                        term TEXT NOT NULL,
                        explanation TEXT NOT NULL,
                        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_simplifications_session 
                    ON simplifications(session_id, timestamp)
                """)
                
                # Summaries table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS summaries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT REFERENCES sessions(id) ON DELETE CASCADE UNIQUE,
                        title TEXT,
                        diagnosis TEXT,
                        medications TEXT,
                        instructions TEXT,
                        follow_up TEXT,
                        key_points TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_summaries_session 
                    ON summaries(session_id)
                """)
                
                await db.commit()
                logger.info("SQLite database initialized successfully")
                
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
            session_id = str(uuid4())
            title = f"Medical Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON")
                await db.execute(
                    "INSERT INTO sessions (id, language, title) VALUES (?, ?, ?)",
                    (session_id, language, title)
                )
                await db.commit()
            
            logger.info(f"Created session: {session_id}")
            return session_id
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
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON")
                await db.execute(
                    "UPDATE sessions SET ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (session_id,)
                )
                await db.commit()
            
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
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON")
                await db.execute(
                    "INSERT INTO transcript_chunks (session_id, text) VALUES (?, ?)",
                    (session_id, text)
                )
                await db.commit()
            
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
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON")
                await db.execute(
                    "INSERT INTO simplifications (session_id, term, explanation) VALUES (?, ?, ?)",
                    (session_id, term, explanation)
                )
                await db.commit()
            
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
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON")
                await db.execute(
                    """
                    INSERT OR REPLACE INTO summaries 
                    (session_id, title, diagnosis, medications, instructions, follow_up, key_points) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        summary.get("title", ""),
                        summary.get("diagnosis", ""),
                        json.dumps(summary.get("medications", [])),
                        json.dumps(summary.get("instructions", [])),
                        summary.get("follow_up", ""),
                        json.dumps(summary.get("key_points", []))
                    )
                )
                await db.commit()
            
            logger.info(f"Saved summary for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
            raise

    async def get_all_sessions(self) -> List[Dict]:
        """
        Retrieve all sessions ordered by created_at descending.
        Includes transcript_count and has_summary for the history list UI.
        """
        try:
            sessions = []
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("""
                    SELECT
                        s.id, s.title, s.language, s.created_at, s.ended_at,
                        COUNT(DISTINCT tc.id)  AS transcript_count,
                        COUNT(DISTINCT su.id)  AS summary_count
                    FROM sessions s
                    LEFT JOIN transcript_chunks tc ON tc.session_id = s.id
                    LEFT JOIN summaries su ON su.session_id = s.id
                    GROUP BY s.id
                    ORDER BY s.created_at DESC
                """) as cursor:
                    async for row in cursor:
                        sessions.append({
                            "id":               row["id"],
                            "title":            row["title"],
                            "language":         row["language"],
                            "created_at":       row["created_at"],
                            "ended_at":         row["ended_at"],
                            "transcript_count": row["transcript_count"],
                            "has_summary":      row["summary_count"] > 0,
                        })
            return sessions
        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            raise

    async def get_session_details(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve complete session data including transcript, simplifications, and summary

        Args:
            session_id: UUID of the session

        Returns:
            Dictionary with session, transcript, simplifications, and summary, or None if not found
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                # Get session
                async with db.execute(
                    "SELECT id, title, language, created_at, ended_at FROM sessions WHERE id = ?",
                    (session_id,)
                ) as cursor:
                    session_row = await cursor.fetchone()
                
                if not session_row:
                    return None
                
                # Get transcript chunks
                transcript = []
                async with db.execute(
                    "SELECT id, session_id, text, timestamp FROM transcript_chunks WHERE session_id = ? ORDER BY timestamp ASC",
                    (session_id,)
                ) as cursor:
                    async for row in cursor:
                        transcript.append({
                            "id": row["id"],
                            "session_id": row["session_id"],
                            "text": row["text"],
                            "timestamp": row["timestamp"]
                        })
                
                # Get simplifications
                simplifications = []
                async with db.execute(
                    "SELECT id, session_id, term, explanation, timestamp FROM simplifications WHERE session_id = ? ORDER BY timestamp ASC",
                    (session_id,)
                ) as cursor:
                    async for row in cursor:
                        simplifications.append({
                            "id": row["id"],
                            "session_id": row["session_id"],
                            "term": row["term"],
                            "explanation": row["explanation"],
                            "timestamp": row["timestamp"]
                        })
                
                # Get summary
                summary = None
                async with db.execute(
                    "SELECT id, session_id, title, diagnosis, medications, instructions, follow_up, key_points, created_at FROM summaries WHERE session_id = ?",
                    (session_id,)
                ) as cursor:
                    summary_row = await cursor.fetchone()
                
                if summary_row:
                    summary = {
                        "id": summary_row["id"],
                        "session_id": summary_row["session_id"],
                        "title": summary_row["title"],
                        "diagnosis": summary_row["diagnosis"],
                        "medications": json.loads(summary_row["medications"]) if summary_row["medications"] else [],
                        "instructions": json.loads(summary_row["instructions"]) if summary_row["instructions"] else [],
                        "follow_up": summary_row["follow_up"],
                        "key_points": json.loads(summary_row["key_points"]) if summary_row["key_points"] else [],
                        "created_at": summary_row["created_at"]
                    }
                
                return {
                    "session": {
                        "id": session_row["id"],
                        "title": session_row["title"],
                        "language": session_row["language"],
                        "created_at": session_row["created_at"],
                        "ended_at": session_row["ended_at"]
                    },
                    "transcript": transcript,
                    "simplifications": simplifications,
                    "summary": summary
                }
                
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
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("PRAGMA foreign_keys = ON")
                await db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                await db.commit()
            
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
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT COUNT(*) FROM simplifications WHERE session_id = ?",
                    (session_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return row[0]
        except Exception as e:
            logger.error(f"Failed to get simplification count: {e}")
            raise
