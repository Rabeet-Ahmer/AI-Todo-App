"""
Session management for agent conversations

Handles SQLite-based conversation context storage using the OpenAI Agents SDK's
SQLiteSession implementation.
"""

import uuid
from pathlib import Path

from agents import SQLiteSession

from .config import get_agent_config


def get_or_create_session(user_id: str, session_id: str | None = None) -> tuple[SQLiteSession, str]:
    """
    Get existing session or create a new one for the user

    Args:
        user_id: Authenticated user ID from request context
        session_id: Optional existing session ID (if continuing conversation)

    Returns:
        Tuple of (SQLiteSession, session_id)
    """
    # Generate new session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())

    # Create session key format: user_{user_id}_session_{session_id}
    session_key = f"user_{user_id}_session_{session_id}"

    # Get session DB path from config
    config = get_agent_config()
    db_path = Path(config.session_db_path)

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create SQLite session
    session = SQLiteSession(session_key, db_path=str(db_path))

    return session, session_id


def clear_session(user_id: str, session_id: str):
    """
    Clear a specific session (useful for explicit reset)

    Note: Session cleanup/expiration will be handled by a background task
    in production (not implemented in MVP)
    """
    # For MVP, we'll just create a new session ID on next request
    # In production, implement a cleanup job that removes old sessions
    pass


def get_session_key(user_id: str, session_id: str) -> str:
    """Get the formatted session key"""
    return f"user_{user_id}_session_{session_id}"
