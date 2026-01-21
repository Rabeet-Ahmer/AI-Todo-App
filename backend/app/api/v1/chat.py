"""
AI Agent Chatbot for Todo Management

This module contains:
- SQLite session management for conversation history
- Function tools that call TodoService
- TodoAgent definition with casual/friendly tone
- Chat router endpoints
"""

import os
import sqlite3
import json
import logging
from dotenv import load_dotenv
from datetime import datetime
from dataclasses import dataclass
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from agents import Agent, Runner, function_tool, RunContextWrapper, OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.services.todo_service import TodoService
from app.core.exceptions import TodoNotFoundException

# Configure logging
logger = logging.getLogger(__name__)

load_dotenv()
# =============================================================================
# SQLite Session Management
# =============================================================================

# Path to SQLite database for agent sessions
SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".agent-sessions")
SESSIONS_DB = os.path.join(SESSIONS_DIR, "sessions.db")

model = OpenAIChatCompletionsModel(
    model = "gemini-2.5-flash",
    openai_client = AsyncOpenAI(api_key=os.getenv("GEMINI_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"),
)

def init_session_db() -> None:
    """Initialize SQLite database and create sessions table if not exists."""
    os.makedirs(SESSIONS_DIR, exist_ok=True)

    conn = sqlite3.connect(SESSIONS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            user_id TEXT PRIMARY KEY,
            session_data TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    logger.info(f"Session database initialized at {SESSIONS_DB}")


def get_user_session(user_id: str) -> Optional[str]:
    """Get existing session data for a user."""
    conn = sqlite3.connect(SESSIONS_DB)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT session_data FROM chat_sessions WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def save_user_session(user_id: str, session_data: str) -> None:
    """Save or update session data for a user."""
    now = datetime.utcnow().isoformat()
    conn = sqlite3.connect(SESSIONS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_sessions (user_id, session_data, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            session_data = excluded.session_data,
            updated_at = excluded.updated_at
    """, (user_id, session_data, now, now))
    conn.commit()
    conn.close()


def clear_user_session(user_id: str) -> None:
    """Clear session data for a user."""
    conn = sqlite3.connect(SESSIONS_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def cleanup_old_sessions() -> int:
    """Delete sessions older than 24 hours. Returns count of deleted sessions."""
    conn = sqlite3.connect(SESSIONS_DB)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM chat_sessions
        WHERE updated_at < datetime('now', '-24 hours')
    """)
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


# Initialize database on module load
init_session_db()


# =============================================================================
# Agent Context
# =============================================================================

@dataclass
class AgentContext:
    """Context passed to agent tools containing user info and database session."""
    user_id: str
    session: AsyncSession


# =============================================================================
# Function Tools (Call TodoService directly)
# =============================================================================

@function_tool
async def create_todo(
    ctx: RunContextWrapper[AgentContext],
    title: str,
    description: Optional[str] = None,
    priority: str = "MEDIUM"
) -> str:
    """
    Create a new todo for the user.

    Args:
        title: The title of the todo (required)
        description: Optional description for more details
        priority: Priority level - LOW, MEDIUM, or HIGH (default: MEDIUM)

    Returns:
        Confirmation message with todo details
    """
    try:
        todo_in = TodoCreate(
            title=title,
            description=description,
            priority=priority.upper()
        )
        todo = await TodoService.create_todo(
            ctx.context.session,
            todo_in,
            ctx.context.user_id
        )
        return f"Created todo #{todo.id}: '{todo.title}' with {todo.priority} priority"
    except Exception as e:
        logger.error(f"Error creating todo: {e}")
        return f"Failed to create todo: {str(e)}"


@function_tool
async def list_todos(ctx: RunContextWrapper[AgentContext]) -> str:
    """
    List all todos for the user.

    Returns:
        A formatted list of all user's todos with their details
    """
    try:
        todos = await TodoService.get_todos(ctx.context.session, ctx.context.user_id)

        if not todos:
            return "You don't have any todos yet!"

        result = f"Found {len(todos)} todo(s):\n\n"
        for todo in todos:
            status = "Done" if todo.completed else "Pending"
            result += f"#{todo.id}: {todo.title} [{todo.priority}] - {status}\n"
            if todo.description:
                result += f"   Description: {todo.description}\n"

        return result
    except Exception as e:
        logger.error(f"Error listing todos: {e}")
        return f"Failed to list todos: {str(e)}"


@function_tool
async def update_todo(
    ctx: RunContextWrapper[AgentContext],
    todo_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None,
    priority: Optional[str] = None
) -> str:
    """
    Update an existing todo.

    Args:
        todo_id: The ID of the todo to update (required)
        title: New title (optional)
        description: New description (optional)
        completed: Mark as complete (True) or incomplete (False) (optional)
        priority: New priority - LOW, MEDIUM, or HIGH (optional)

    Returns:
        Confirmation message with updated details
    """
    try:
        todo_update = TodoUpdate(
            title=title,
            description=description,
            completed=completed,
            priority=priority.upper() if priority else None
        )

        todo = await TodoService.update_todo(
            ctx.context.session,
            todo_id,
            todo_update,
            ctx.context.user_id
        )

        changes = []
        if title:
            changes.append(f"title to '{title}'")
        if description:
            changes.append(f"description")
        if completed is not None:
            changes.append("marked as complete" if completed else "marked as incomplete")
        if priority:
            changes.append(f"priority to {priority.upper()}")

        change_str = ", ".join(changes) if changes else "no changes"
        return f"Updated todo #{todo.id}: {change_str}"

    except TodoNotFoundException:
        return f"Couldn't find todo #{todo_id}. Want me to show your list?"
    except Exception as e:
        logger.error(f"Error updating todo: {e}")
        return f"Failed to update todo: {str(e)}"


@function_tool
async def delete_todo(ctx: RunContextWrapper[AgentContext], todo_id: int) -> str:
    """
    Delete a todo.

    Args:
        todo_id: The ID of the todo to delete (required)

    Returns:
        Confirmation message
    """
    try:
        await TodoService.delete_todo(
            ctx.context.session,
            todo_id,
            ctx.context.user_id
        )
        return f"Deleted todo #{todo_id}"
    except TodoNotFoundException:
        return f"Couldn't find todo #{todo_id}. Want me to show your list?"
    except Exception as e:
        logger.error(f"Error deleting todo: {e}")
        return f"Failed to delete todo: {str(e)}"


@function_tool
async def get_stats(ctx: RunContextWrapper[AgentContext]) -> str:
    """
    Get todo statistics for the user.

    Returns:
        Summary of total, pending, and completed todos
    """
    try:
        stats = await TodoService.get_stats(ctx.context.session, ctx.context.user_id)
        return f"You have {stats.total} total todos: {stats.pending} pending, {stats.completed} completed"
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return f"Failed to get stats: {str(e)}"


# =============================================================================
# Agent Definition
# =============================================================================

AGENT_INSTRUCTIONS = """
You are a friendly todo assistant! Help users manage their todos through casual conversation.

What you can do:
- Create new todos (with title, description, priority: LOW/MEDIUM/HIGH)
- Show all todos
- Update todos (title, description, mark complete/incomplete, change priority)
- Delete todos
- Show stats (total, pending, completed counts)

Your style:
- Be casual and friendly ("Done!", "Got it!", "Here you go!")
- Keep responses short and helpful
- Confirm actions with brief messages like "Added 'Buy groceries' to your list!"
- When creating todos, extract the title from what the user says
- Default priority is MEDIUM unless they mention urgency
- If you need a todo ID for updates/deletes, list their todos first
- If something's unclear, ask a quick clarifying question

Example responses:
- "Done! I've added 'Call mom' to your list."
- "Here are your 5 todos..."
- "Got it! Marked 'Buy groceries' as complete."
- "Hmm, which task did you mean? Here's your list..."
"""

todo_agent = Agent(
    name="TodoAgent",
    instructions=AGENT_INSTRUCTIONS,
    tools=[create_todo, list_todos, update_todo, delete_todo, get_stats],
    model = model
)


# =============================================================================
# FastAPI Router
# =============================================================================

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db_session: Annotated[AsyncSession, Depends(get_session)]
):
    """
    Send a message to the AI agent and get a response.

    The agent can help with:
    - Creating todos
    - Listing todos
    - Updating todos
    - Deleting todos
    - Getting statistics
    """
    try:
        # Create agent context with user info and database session
        context = AgentContext(
            user_id=current_user.id,
            session=db_session
        )

        # Load existing conversation history for this user
        session_data = get_user_session(current_user.id)

        # Run the agent
        # Note: OpenAI Agents SDK handles conversation history internally
        # We pass the previous messages if available
        if session_data:
            # Parse previous conversation
            history = json.loads(session_data)
            # Add new user message
            history.append({"role": "user", "content": request.content})

            # Run with history
            result = await Runner.run(
                todo_agent,
                history,
                context=context
            )
        else:
            # First message - no history
            result = await Runner.run(
                todo_agent,
                request.content,
                context=context
            )

        # Get the final output
        final_output = result.final_output

        # Save updated conversation history
        # Get conversation from result or build it
        new_history = []
        if session_data:
            new_history = json.loads(session_data)
        new_history.append({"role": "user", "content": request.content})
        new_history.append({"role": "assistant", "content": final_output})

        # Keep only last 20 messages to prevent token overflow
        if len(new_history) > 20:
            new_history = new_history[-20:]

        save_user_session(current_user.id, json.dumps(new_history))

        return ChatResponse(message=final_output)

    except Exception as e:
        logger.error(f"Chat error for user {current_user.id}: {e}", exc_info=True)
        # Return user-friendly error message
        return ChatResponse(
            message="Sorry, I couldn't complete that. Please try again!"
        )


@router.delete("/session")
async def clear_chat_session(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Clear the chat history for the current user."""
    clear_user_session(current_user.id)
    return {"message": "Chat history cleared"}


@router.get("/health")
async def chat_health():
    """Health check for chat service."""
    return {"status": "healthy", "service": "chat"}
