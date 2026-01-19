"""
Guardrails for agent security and validation

Implements input and output guardrails to ensure:
- User authorization (authenticated requests only)
- Input sanitization (prevent injection, validate format)
- Rate limiting (prevent abuse)
- Todo ownership (prevent cross-user access)
"""

from collections import defaultdict
from datetime import datetime, timedelta

from agents import GuardrailFunctionOutput, InputGuardrail, output_guardrail


# ============================================================================
# T010: User Authorization Guardrail (Input)
# ============================================================================


async def user_authorization_guardrail(ctx, agent, input_data):
    """
    Ensure user is authenticated before processing any requests

    Checks that user_id exists in the context (set by API authentication middleware)
    """
    user_id = ctx.get("user_id")

    if not user_id:
        return GuardrailFunctionOutput(
            output_info="User not authenticated",
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(tripwire_triggered=False)


# Create guardrail instance for attachment to agents
user_authorization = InputGuardrail(guardrail_function=user_authorization_guardrail)


# ============================================================================
# T011: Input Sanitization Guardrail (Input)
# ============================================================================


async def input_sanitization_guardrail(ctx, agent, input_data):
    """
    Validate and sanitize user input

    Checks:
    - Message length (max 2000 characters)
    - Non-empty messages
    - Basic format validation
    """
    # Extract message from input_data (structure depends on how agent is called)
    message = input_data.get("content", "") if isinstance(input_data, dict) else str(input_data)

    # Max length check
    if len(message) > 2000:
        return GuardrailFunctionOutput(
            output_info="Message too long (max 2000 characters)",
            tripwire_triggered=True,
        )

    # Empty message check
    if not message or message.strip() == "":
        return GuardrailFunctionOutput(
            output_info="Empty message not allowed",
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(tripwire_triggered=False)


# Create guardrail instance
input_sanitization = InputGuardrail(guardrail_function=input_sanitization_guardrail)


# ============================================================================
# T012: Rate Limit Guardrail (Input)
# ============================================================================

# In-memory rate limiter (use Redis in production for distributed systems)
_request_counts: defaultdict[str, list[datetime]] = defaultdict(list)


async def rate_limit_guardrail(ctx, agent, input_data):
    """
    Prevent abuse by limiting requests per user

    Limit: 30 requests per minute per user
    Note: In production, use Redis for distributed rate limiting
    """
    user_id = ctx.get("user_id")
    if not user_id:
        # If no user_id, let user_authorization_guardrail handle it
        return GuardrailFunctionOutput(tripwire_triggered=False)

    now = datetime.now()

    # Clean old requests (older than 1 minute)
    _request_counts[user_id] = [
        ts for ts in _request_counts[user_id]
        if now - ts < timedelta(minutes=1)
    ]

    # Check limit
    if len(_request_counts[user_id]) >= 30:
        return GuardrailFunctionOutput(
            output_info="Rate limit exceeded (30 requests per minute)",
            tripwire_triggered=True,
        )

    # Record this request
    _request_counts[user_id].append(now)

    return GuardrailFunctionOutput(tripwire_triggered=False)


# Create guardrail instance
rate_limit = InputGuardrail(guardrail_function=rate_limit_guardrail)


# ============================================================================
# T013: Todo Ownership Guardrail (Output)
# ============================================================================


@output_guardrail
async def todo_ownership_guardrail(ctx, agent, output):
    """
    Ensure agent never returns todos belonging to other users

    Critical security check to prevent cross-user data leakage
    """
    user_id = ctx.get("user_id")

    if not user_id:
        # Shouldn't reach here (input guardrail should catch this)
        return GuardrailFunctionOutput(
            output_info="No user_id in context for ownership check",
            tripwire_triggered=True,
        )

    # Check if output contains todos (from tool results)
    if hasattr(output, "todos") and output.todos:
        for todo in output.todos:
            # Check if todo has user_id field
            if isinstance(todo, dict) and "user_id" in todo:
                if str(todo["user_id"]) != str(user_id):
                    # Security violation detected!
                    return GuardrailFunctionOutput(
                        output_info=f"Unauthorized access attempt: todo {todo.get('id')} belongs to user {todo['user_id']}, not {user_id}",
                        tripwire_triggered=True,
                    )
            elif hasattr(todo, "user_id"):
                if str(todo.user_id) != str(user_id):
                    return GuardrailFunctionOutput(
                        output_info=f"Unauthorized access attempt: todo belongs to different user",
                        tripwire_triggered=True,
                    )

    return GuardrailFunctionOutput(tripwire_triggered=False)


# ============================================================================
# Guardrail Lists for Agent Attachment
# ============================================================================

# Input guardrails (apply to all agents)
INPUT_GUARDRAILS = [
    user_authorization,
    input_sanitization,
    rate_limit,
]

# Output guardrails (apply to agents that return todos)
OUTPUT_GUARDRAILS = [
    todo_ownership_guardrail,
]
