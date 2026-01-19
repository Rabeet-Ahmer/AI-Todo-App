"""
Chat API endpoints for AI Agent interaction

Provides endpoints for natural language todo management via OpenAI Agents SDK.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.v1.deps import get_current_user
from app.main_agents.runner import run_agent, check_agent_health
from app.models.user import User

router = APIRouter(prefix="/chat", tags=["chat"])


# ============================================================================
# Request/Response Models
# ============================================================================


class ChatMessageRequest(BaseModel):
    """Request model for chat messages"""

    message: str = Field(..., min_length=1, max_length=2000, description="User's message to the agent")
    session_id: str | None = Field(None, description="Optional session ID for conversation continuity")


class ChatMessageResponse(BaseModel):
    """Response model for chat messages"""

    success: bool
    message: str = Field(..., description="Agent's natural language response")
    action_performed: str | None = Field(None, description="Action that was performed (create/read/update/delete/query/none)")
    todos_affected: list[int] | None = Field(None, description="IDs of todos created or modified")
    clarification_needed: bool = Field(default=False)
    clarification_prompt: str | None = None
    session_id: str = Field(..., description="Session ID for this conversation")


class ChatErrorResponse(BaseModel):
    """Error response model"""

    success: bool = False
    error: str
    error_code: str
    session_id: str | None = None


class AgentHealthResponse(BaseModel):
    """Health check response for agent system"""

    healthy: bool
    model: str | None = None
    max_turns: int | None = None
    agent_name: str | None = None
    error: str | None = None


# ============================================================================
# T030: POST /api/v1/chat/message endpoint
# ============================================================================


@router.post("/message", response_model=ChatMessageResponse, status_code=status.HTTP_200_OK)
async def send_message(
    request: ChatMessageRequest,
    current_user: Annotated[User, Depends(get_current_user)],  # T031: Extract user_id from auth
) -> ChatMessageResponse | ChatErrorResponse:
    """
    Send a message to the AI agent for todo management

    The agent can:
    - Create todos from natural language
    - Update existing todos
    - Delete todos
    - Query and filter todos
    - Provide statistics

    Authentication required via Bearer token.

    Args:
        request: Chat message and optional session ID
        current_user: Authenticated user from JWT token

    Returns:
        Agent's response with action details and session ID

    Raises:
        HTTPException: 401 if not authenticated (handled by dependency)
        HTTPException: 403 if guardrails block the request
        HTTPException: 429 if rate limit exceeded
        HTTPException: 500 for internal errors
    """
    # T032: Create or retrieve session
    # T033: Pass user_id context to Runner.run()
    # T034: Return ChatResponse with structured fields
    # T035: Add error handling for guardrail triggers

    result = await run_agent(
        user_id=current_user.id,  # user_id is string (Better Auth UUID)
        message=request.message,
        session_id=request.session_id,
    )

    if not result["success"]:
        error_code = result["error_code"]
        error_message = result["error"]

        # Map error codes to HTTP status codes
        if error_code == "auth_error":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_message,
            )
        elif error_code == "rate_limit":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_message,
            )
        elif error_code == "invalid_input":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=error_message,
            )
        elif error_code in ["security_error", "guardrail_error"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error_message,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_message,
            )

    # Extract structured response from agent
    agent_response = result["response"]

    return ChatMessageResponse(
        success=True,
        message=agent_response.message,
        action_performed=agent_response.action_performed,
        todos_affected=agent_response.todos_affected,
        clarification_needed=agent_response.clarification_needed,
        clarification_prompt=agent_response.clarification_prompt,
        session_id=result["session_id"],
    )


# ============================================================================
# Health Check Endpoint
# ============================================================================


@router.get("/health", response_model=AgentHealthResponse)
async def agent_health() -> AgentHealthResponse:
    """
    Check agent system health

    Verifies:
    - OpenAI API key is configured
    - Agents can be initialized
    - Configuration is valid

    No authentication required.
    """
    health_status = check_agent_health()
    return AgentHealthResponse(**health_status)
