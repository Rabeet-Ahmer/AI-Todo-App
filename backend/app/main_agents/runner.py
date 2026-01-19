"""
Agent execution wrapper

Handles running agents with proper:
- Session management
- Context passing (user_id)
- Exception handling
- Logging
"""

import logging
from typing import Any

from agents import Runner
from agents.exceptions import (
    InputGuardrailTripwireTriggered,
    MaxTurnsExceeded,
    ModelBehaviorError,
    OutputGuardrailTripwireTriggered,
)

from .agents import get_todo_manager_agent
from .config import get_agent_config
from .models import ChatResponse
from .sessions import get_or_create_session

logger = logging.getLogger(__name__)


# ============================================================================
# T028: Implement agent runner function with session management
# ============================================================================


async def run_agent(
    user_id: str,
    message: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Run the TodoManagerAgent with a user message

    Args:
        user_id: Authenticated user ID from request
        message: User's natural language message
        session_id: Optional existing session ID (for conversation continuity)

    Returns:
        Dict containing:
        - success: bool
        - response: ChatResponse | None
        - session_id: str
        - error: str | None (if success=False)
        - error_code: str | None (e.g., "auth_error", "rate_limit", etc.)
    """
    config = get_agent_config()

    try:
        # Get or create session
        session, session_id = get_or_create_session(user_id, session_id)

        # Get TodoManager agent (entry point)
        agent = get_todo_manager_agent()

        # Prepare context with user_id (for guardrails and tools)
        context = {
            "user_id": user_id,
        }

        # T077: Run agent with session and context (supports handoffs automatically)
        result = await Runner.run(
            agent,
            input=message,
            session=session,
            context=context,
            max_turns=config.max_turns,
        )

        # T078: Log handoff events (if any occurred)
        # Note: In production, check result for handoff events and log them
        # The SDK handles handoffs internally via the handoffs list

        # Extract final output (should be ChatResponse due to output_type)
        response = result.final_output

        return {
            "success": True,
            "response": response,
            "session_id": session_id,
            "error": None,
            "error_code": None,
        }

    # T029: Exception handling for guardrails and errors
    except InputGuardrailTripwireTriggered as e:
        logger.warning(f"Input guardrail triggered for user {user_id}: {e}")

        # Determine error code based on guardrail type
        error_message = str(e)
        if "not authenticated" in error_message.lower():
            error_code = "auth_error"
        elif "rate limit" in error_message.lower():
            error_code = "rate_limit"
        elif "too long" in error_message.lower() or "empty" in error_message.lower():
            error_code = "invalid_input"
        else:
            error_code = "guardrail_error"

        return {
            "success": False,
            "response": None,
            "session_id": session_id,
            "error": error_message,
            "error_code": error_code,
        }

    except OutputGuardrailTripwireTriggered as e:
        logger.error(f"Output guardrail triggered for user {user_id}: {e}")
        # Security violation - log but don't reveal details to user
        return {
            "success": False,
            "response": None,
            "session_id": session_id,
            "error": "Unable to process request due to security policy",
            "error_code": "security_error",
        }

    except MaxTurnsExceeded:
        logger.warning(f"Max turns exceeded for user {user_id}, session {session_id}")
        return {
            "success": False,
            "response": None,
            "session_id": session_id,
            "error": "Conversation too long. Please start a new session.",
            "error_code": "max_turns",
        }

    except ModelBehaviorError as e:
        logger.error(f"Model behavior error for user {user_id}: {e}")
        return {
            "success": False,
            "response": None,
            "session_id": session_id,
            "error": "The agent encountered an error. Please try again.",
            "error_code": "model_error",
        }

    except Exception as e:
        logger.exception(f"Unexpected error running agent for user {user_id}: {e}")
        return {
            "success": False,
            "response": None,
            "session_id": session_id,
            "error": "An unexpected error occurred. Please try again.",
            "error_code": "internal_error",
        }


# ============================================================================
# Health Check
# ============================================================================


def check_agent_health() -> dict[str, Any]:
    """
    Check if agents are properly configured and can be initialized

    Returns status dict with any configuration issues
    """
    try:
        config = get_agent_config()

        # Check API key
        if not config.openai_api_key or config.openai_api_key == "your-api-key-here":
            return {
                "healthy": False,
                "error": "OPENAI_API_KEY not configured",
            }

        # Try to initialize agents
        agent = get_todo_manager_agent()

        return {
            "healthy": True,
            "model": config.openai_model,
            "max_turns": config.max_turns,
            "agent_name": agent.name,
        }

    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
        }
