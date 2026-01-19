"""
Agent definitions for todo management

Defines the TodoManagerAgent and AnalyticsAgent with their:
- Instructions (system prompts)
- Tools (function tools they can call)
- Guardrails (security/validation)
- Handoffs (agent-to-agent routing)
"""

from agents import Agent
from agents.model_settings import ModelSettings
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from .guardrails import INPUT_GUARDRAILS, OUTPUT_GUARDRAILS
from .models import ChatResponse
from .tools import (
    create_todo,
    delete_todo,
    filter_todos_by_date,
    filter_todos_by_status,
    get_todo_statistics,
    get_todos,
    search_todos,
    update_todo,
)
from .config import get_agent_config


# ============================================================================
# Gemini Model Configuration
# ============================================================================

def create_gemini_model():
    """Create Gemini model via OpenAI compatibility layer"""
    config = get_agent_config()

    external_client = AsyncOpenAI(
        api_key=config.gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    return OpenAIChatCompletionsModel(
        model=config.gemini_model,
        openai_client=external_client
    )


# ============================================================================
# TodoManagerAgent
# ============================================================================

TODO_MANAGER_INSTRUCTIONS = """
You are a helpful Todo Management Assistant. Your job is to help users manage their todo list through natural conversation.

**Creating Todos:**
When users ask to create todos, extract:
- Title (required) - be concise but clear
- Description (optional) - additional details if mentioned
- Due date (optional) - parse natural language like "tomorrow", "next Friday", "in 3 days", "end of week"
- Priority (low/medium/high) - default to medium if not specified

Examples:
- "Add a task to buy groceries" → title: "Buy groceries", priority: medium
- "Remind me to call John tomorrow" → title: "Call John", due_date: tomorrow
- "High priority: finish the report by Friday" → title: "Finish the report", due_date: next Friday, priority: high

**Updating Todos:**
When users want to update todos, identify which todo they're referring to by matching keywords to todo titles.
If multiple matches, ask which one they mean.

Examples:
- "Mark the grocery task as done" → find todo with "grocery" in title, set status to completed
- "Change the report deadline to next Monday" → find "report" todo, update due_date

**Deleting Todos:**
Always confirm before deleting (ask: "Are you sure you want to delete {todo_title}?")

**Queries:**
For complex analytics questions like "What's due this week?", "Show overdue tasks", or "How many tasks have I completed?",
hand off to the AnalyticsAgent who specializes in queries and reporting.

**Clarification:**
If the request is ambiguous, ask ONE clarifying question at a time. Be concise and friendly.

Always confirm successful operations to the user with a clear message.
"""


# ============================================================================
# AnalyticsAgent
# ============================================================================

ANALYTICS_AGENT_INSTRUCTIONS = """
You are a Todo Analytics Specialist. When users ask questions about their todos, provide clear, data-driven answers.

**Date-based Queries:**
Use the filter_todos_by_date tool for questions about:
- "today" - todos due today
- "tomorrow" - todos due tomorrow
- "this week" - todos due this week
- "overdue" - todos past their due date

**Status Queries:**
Use filter_todos_by_status for:
- "pending" or "incomplete" todos
- "completed" or "done" todos

**Statistics:**
Use get_todo_statistics for summary questions like:
- "How many tasks do I have?"
- "What's my completion rate?"
- "How many overdue tasks?"

**Presentation:**
Present results in a friendly, conversational way. For lists, format them clearly:
- Use bullet points or numbers
- Include key details (title, due date, priority)
- Highlight important information (overdue in urgent tone)

After answering, if the user wants to take action (create, update, delete), let them know they can just ask and the system will handle it.
"""


# ============================================================================
# Agent Creation
# ============================================================================

async def run_agent_query(
    user_message: str,
    user_id: str,
    session_id: str | None = None
) -> ChatResponse:
    """Run the agent with session management and return structured output"""
    from .sessions import get_or_create_session
    from agents import Runner

    session, session_id = get_or_create_session(user_id, session_id)
    agent = get_todo_manager_agent()

    response = await Runner.run(
        agent,
        user_message,
        session=session
    )

    return ChatResponse(
        agent_name=response.agent_name,
        response=response.output,
        session_id=session_id
    )


def get_todo_manager_agent():
    """Get or create the TodoManagerAgent instance with handoff to AnalyticsAgent"""
    global _todo_manager_agent, _analytics_agent

    if _todo_manager_agent is None:
        # First create AnalyticsAgent
        _analytics_agent = Agent(
            name="AnalyticsAgent",
            model=create_gemini_model(),
            instructions=ANALYTICS_AGENT_INSTRUCTIONS,
            tools=[
                filter_todos_by_date,
                filter_todos_by_status,
                get_todo_statistics,
                get_todos,
            ],
            input_guardrails=INPUT_GUARDRAILS,
            output_guardrails=OUTPUT_GUARDRAILS,
            output_type=ChatResponse,
        )

        # Then create TodoManagerAgent with handoff
        _todo_manager_agent = Agent(
            name="TodoManagerAgent",
            model=create_gemini_model(),
            instructions=TODO_MANAGER_INSTRUCTIONS,
            tools=[
                create_todo,
                get_todos,
                update_todo,
                delete_todo,
                search_todos,
            ],
            input_guardrails=INPUT_GUARDRAILS,
            output_guardrails=OUTPUT_GUARDRAILS,
            output_type=ChatResponse,
            handoffs=[_analytics_agent],
        )

    return _todo_manager_agent


def get_analytics_agent():
    """Get or create the AnalyticsAgent instance"""
    global _analytics_agent

    if _analytics_agent is None:
        # This will create both agents and setup handoffs
        get_todo_manager_agent()

    return _analytics_agent


# Global agent instances (created once)
_todo_manager_agent = None
_analytics_agent = None


__all__ = [
    "get_todo_manager_agent",
    "get_analytics_agent",
    "run_agent_query",
]
