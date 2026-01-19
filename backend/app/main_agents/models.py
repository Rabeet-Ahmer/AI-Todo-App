"""
Pydantic models for agent tool inputs and outputs

These models define the structured schemas for all agent function tools.
They ensure type safety and validation for agent interactions.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ============================================================================
# User Story 1: Natural Language Todo Creation
# ============================================================================


class CreateTodoInput(BaseModel):
    """Input schema for create_todo tool"""

    title: str = Field(..., description="Todo title extracted from user message")
    description: str | None = Field(
        None, description="Optional description/details about the todo"
    )
    due_date: datetime | None = Field(
        None,
        description="Due date parsed from natural language (e.g., 'tomorrow', 'next Friday')",
    )
    priority: Literal["low", "medium", "high"] = Field(
        default="medium", description="Priority level (default: medium)"
    )


class CreateTodoOutput(BaseModel):
    """Output schema for create_todo tool"""

    success: bool
    todo_id: int | None = None
    message: str


class GetTodosOutput(BaseModel):
    """Output schema for get_todos tool (no input needed)"""

    success: bool
    todos: list[dict]  # List of todo dictionaries (will use TodoSchema from API)
    message: str


# ============================================================================
# User Story 2: Todo Management via Chat
# ============================================================================


class UpdateTodoInput(BaseModel):
    """Input schema for update_todo tool"""

    todo_id: int = Field(..., description="ID of the todo to update")
    title: str | None = Field(None, description="New title (optional)")
    description: str | None = Field(None, description="New description (optional)")
    due_date: datetime | None = Field(None, description="New due date (optional)")
    status: Literal["pending", "completed"] | None = Field(
        None, description="New status (optional)"
    )
    priority: Literal["low", "medium", "high"] | None = Field(
        None, description="New priority (optional)"
    )


class UpdateTodoOutput(BaseModel):
    """Output schema for update_todo tool"""

    success: bool
    message: str


class DeleteTodoInput(BaseModel):
    """Input schema for delete_todo tool"""

    todo_id: int = Field(..., description="ID of the todo to delete")


class DeleteTodoOutput(BaseModel):
    """Output schema for delete_todo tool"""

    success: bool
    message: str


class SearchTodosInput(BaseModel):
    """Input schema for search_todos tool"""

    query: str = Field(
        ...,
        description="Search query to match against todo titles and descriptions",
    )


class SearchTodosOutput(BaseModel):
    """Output schema for search_todos tool"""

    success: bool
    todos: list[dict]
    message: str


# ============================================================================
# User Story 3: Conversational Todo Queries (AnalyticsAgent)
# ============================================================================


class FilterByDateInput(BaseModel):
    """Input schema for filter_todos_by_date tool"""

    filter_type: Literal["today", "tomorrow", "this_week", "overdue"] = Field(
        ..., description="Type of date filter to apply"
    )


class FilterByDateOutput(BaseModel):
    """Output schema for filter_todos_by_date tool"""

    success: bool
    todos: list[dict]
    count: int
    message: str


class FilterByStatusInput(BaseModel):
    """Input schema for filter_todos_by_status tool"""

    status: Literal["pending", "completed"] = Field(
        ..., description="Status to filter by"
    )


class FilterByStatusOutput(BaseModel):
    """Output schema for filter_todos_by_status tool"""

    success: bool
    todos: list[dict]
    count: int
    message: str


class TodoStatsOutput(BaseModel):
    """Output schema for get_todo_statistics tool"""

    total: int
    completed: int
    pending: int
    overdue: int
    message: str


# ============================================================================
# Agent Output Models (Structured Outputs)
# ============================================================================


class ChatResponse(BaseModel):
    """Main structured output for agent responses"""

    message: str = Field(..., description="Natural language response to user")
    action_performed: Literal[
        "create", "read", "update", "delete", "query", "none"
    ] | None = Field(
        None, description="Action that was performed (if any)"
    )
    todos_affected: list[int] | None = Field(
        None, description="IDs of todos that were created or modified"
    )
    clarification_needed: bool = Field(
        default=False, description="Whether agent needs clarification from user"
    )
    clarification_prompt: str | None = Field(
        None, description="Question to ask user if clarification needed"
    )
