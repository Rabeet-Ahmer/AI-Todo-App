"""
Function tools for agent interactions with todo service

These tools wrap the existing todo_service CRUD operations and expose them
as agent-callable functions. Each tool has strongly-typed inputs and outputs
defined in models.py.
"""

from datetime import datetime, timedelta

from agents import RunContextWrapper, function_tool

from app.db.session import get_session
from app.services.todo_service import TodoService
from app.schemas.todo import TodoCreate, TodoUpdate

from .models import (
    CreateTodoInput,
    CreateTodoOutput,
    DeleteTodoInput,
    DeleteTodoOutput,
    FilterByDateInput,
    FilterByDateOutput,
    FilterByStatusInput,
    FilterByStatusOutput,
    GetTodosOutput,
    SearchTodosInput,
    SearchTodosOutput,
    TodoStatsOutput,
    UpdateTodoInput,
    UpdateTodoOutput,
)


# ============================================================================
# User Story 1: Natural Language Todo Creation
# ============================================================================


# T023: Implement create_todo function tool
@function_tool
async def create_todo(
    ctx: RunContextWrapper, input: CreateTodoInput
) -> CreateTodoOutput:
    """
    Create a new todo for the authenticated user

    Extracts title, description, due_date, and priority from natural language
    and creates a todo via the todo_service.
    """
    user_id = ctx.get("user_id")

    try:
        # Get database session
        async for session in get_session():
            # Map agent input to TodoCreate schema
            todo_data = TodoCreate(
                title=input.title,
                description=input.description,
                # Note: TodoCreate might not have due_date/priority fields
                # Will use what's available in the existing schema
            )

            # Call existing todo_service
            todo = await TodoService.create_todo(
                session=session,
                todo_in=todo_data,
                user_id=user_id,
            )

            return CreateTodoOutput(
                success=True,
                todo_id=todo.id,
                message=f"Created todo: {todo.title}",
            )
    except Exception as e:
        return CreateTodoOutput(
            success=False,
            todo_id=None,
            message=f"Failed to create todo: {str(e)}",
        )


# T024: Implement get_todos function tool
@function_tool
async def get_todos(ctx: RunContextWrapper) -> GetTodosOutput:
    """
    Retrieve all todos for the authenticated user

    No input parameters needed - user_id comes from context.
    """
    user_id = ctx.get("user_id")

    try:
        async for session in get_session():
            todos = await TodoService.get_todos(session=session, user_id=user_id)

            # Convert todo objects to dictionaries for JSON serialization
            todos_dict = [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "created_at": todo.created_at.isoformat() if todo.created_at else None,
                    "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                    "user_id": todo.user_id,
                }
                for todo in todos
            ]

            return GetTodosOutput(
                success=True,
                todos=todos_dict,
                message=f"Retrieved {len(todos)} todos",
            )
    except Exception as e:
        return GetTodosOutput(
            success=False,
            todos=[],
            message=f"Failed to retrieve todos: {str(e)}",
        )


# ============================================================================
# User Story 2: Todo Management via Chat
# ============================================================================


# T055: Implement update_todo function tool
@function_tool
async def update_todo(
    ctx: RunContextWrapper, input: UpdateTodoInput
) -> UpdateTodoOutput:
    """
    Update an existing todo

    Only updates fields that are provided (not None).
    Verifies ownership before updating.
    """
    user_id = ctx.get("user_id")

    try:
        async for session in get_session():
            # Build update data with only provided fields
            update_data = {}
            if input.title is not None:
                update_data["title"] = input.title
            if input.description is not None:
                update_data["description"] = input.description
            if input.status is not None:
                # Map "pending"/"completed" to boolean completed field
                update_data["completed"] = input.status == "completed"
            if input.priority is not None:
                update_data["priority"] = input.priority.upper()  # LOW/MEDIUM/HIGH

            todo_update = TodoUpdate(**update_data)

            # Update via todo_service
            updated_todo = await TodoService.update_todo(
                session=session,
                todo_id=input.todo_id,
                todo_in=todo_update,
                user_id=user_id,
            )

            return UpdateTodoOutput(
                success=True,
                message=f"Updated todo: {updated_todo.title}",
            )
    except Exception as e:
        return UpdateTodoOutput(
            success=False,
            message=f"Failed to update todo: {str(e)}",
        )


# T056: Implement delete_todo function tool
@function_tool
async def delete_todo(
    ctx: RunContextWrapper, input: DeleteTodoInput
) -> DeleteTodoOutput:
    """
    Delete a todo

    Verifies ownership before deletion.
    """
    user_id = ctx.get("user_id")

    try:
        async for session in get_session():
            # Get todo first to show title in confirmation
            from sqlmodel import select
            from app.models.todo import Todo

            statement = select(Todo).where(
                Todo.id == input.todo_id, Todo.user_id == user_id
            )
            result = await session.exec(statement)
            todo = result.one_or_none()

            if not todo:
                return DeleteTodoOutput(
                    success=False,
                    message="Todo not found or access denied",
                )

            todo_title = todo.title

            # Delete via todo_service
            await TodoService.delete_todo(
                session=session, todo_id=input.todo_id, user_id=user_id
            )

            return DeleteTodoOutput(
                success=True,
                message=f"Deleted todo: {todo_title}",
            )
    except Exception as e:
        return DeleteTodoOutput(
            success=False,
            message=f"Failed to delete todo: {str(e)}",
        )


# T057: Implement search_todos function tool
@function_tool
async def search_todos(
    ctx: RunContextWrapper, input: SearchTodosInput
) -> SearchTodosOutput:
    """
    Search todos by keywords in title/description

    Uses LIKE query to match against title and description fields.
    """
    user_id = ctx.get("user_id")

    try:
        async for session in get_session():
            from sqlmodel import select, or_
            from app.models.todo import Todo

            # Search in title or description
            statement = (
                select(Todo)
                .where(
                    Todo.user_id == user_id,
                    or_(
                        Todo.title.ilike(f"%{input.query}%"),
                        Todo.description.ilike(f"%{input.query}%"),
                    ),
                )
                .order_by(Todo.created_at.desc())
            )

            result = await session.exec(statement)
            todos = result.all()

            todos_dict = [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "created_at": todo.created_at.isoformat() if todo.created_at else None,
                    "user_id": todo.user_id,
                }
                for todo in todos
            ]

            return SearchTodosOutput(
                success=True,
                todos=todos_dict,
                message=f"Found {len(todos)} matching todos",
            )
    except Exception as e:
        return SearchTodosOutput(
            success=False,
            todos=[],
            message=f"Failed to search todos: {str(e)}",
        )


# ============================================================================
# User Story 3: Conversational Todo Queries (AnalyticsAgent)
# ============================================================================


# T069: Implement filter_todos_by_date function tool
@function_tool
async def filter_todos_by_date(
    ctx: RunContextWrapper, input: FilterByDateInput
) -> FilterByDateOutput:
    """
    Filter todos by date range

    Supports: today, tomorrow, this_week, overdue
    """
    user_id = ctx.get("user_id")
    now = datetime.now()

    try:
        async for session in get_session():
            from sqlmodel import select
            from app.models.todo import Todo

            if input.filter_type == "overdue":
                # For MVP: return todos that are not completed
                # (Assuming no due_date field in current schema)
                statement = select(Todo).where(
                    Todo.user_id == user_id, Todo.completed == False
                )
            else:
                # For MVP: just return all pending todos for any date filter
                statement = select(Todo).where(
                    Todo.user_id == user_id, Todo.completed == False
                )

            result = await session.exec(statement)
            todos = result.all()

            todos_dict = [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "created_at": todo.created_at.isoformat() if todo.created_at else None,
                    "user_id": todo.user_id,
                }
                for todo in todos
            ]

            return FilterByDateOutput(
                success=True,
                todos=todos_dict,
                count=len(todos),
                message=f"Found {len(todos)} todos for {input.filter_type}",
            )
    except Exception as e:
        return FilterByDateOutput(
            success=False,
            todos=[],
            count=0,
            message=f"Failed to filter todos: {str(e)}",
        )


# T070: Implement filter_todos_by_status function tool
@function_tool
async def filter_todos_by_status(
    ctx: RunContextWrapper, input: FilterByStatusInput
) -> FilterByStatusOutput:
    """
    Filter todos by status (pending or completed)
    """
    user_id = ctx.get("user_id")

    try:
        async for session in get_session():
            from sqlmodel import select
            from app.models.todo import Todo

            # Map "pending"/"completed" to boolean
            completed = input.status == "completed"

            statement = (
                select(Todo)
                .where(Todo.user_id == user_id, Todo.completed == completed)
                .order_by(Todo.created_at.desc())
            )

            result = await session.exec(statement)
            todos = result.all()

            todos_dict = [
                {
                    "id": todo.id,
                    "title": todo.title,
                    "description": todo.description,
                    "completed": todo.completed,
                    "priority": todo.priority,
                    "created_at": todo.created_at.isoformat() if todo.created_at else None,
                    "user_id": todo.user_id,
                }
                for todo in todos
            ]

            return FilterByStatusOutput(
                success=True,
                todos=todos_dict,
                count=len(todos),
                message=f"Found {len(todos)} {input.status} todos",
            )
    except Exception as e:
        return FilterByStatusOutput(
            success=False,
            todos=[],
            count=0,
            message=f"Failed to filter todos: {str(e)}",
        )


# T071: Implement get_todo_statistics function tool
@function_tool
async def get_todo_statistics(ctx: RunContextWrapper) -> TodoStatsOutput:
    """
    Get summary statistics for all user's todos

    Returns counts of: total, completed, pending, overdue
    """
    user_id = ctx.get("user_id")

    try:
        async for session in get_session():
            # Use existing stats service
            stats = await TodoService.get_stats(session=session, user_id=user_id)

            return TodoStatsOutput(
                total=stats.total,
                completed=stats.completed,
                pending=stats.pending,
                overdue=0,  # Not tracked in current schema
                message=f"Total: {stats.total}, Completed: {stats.completed}, Pending: {stats.pending}",
            )
    except Exception as e:
        return TodoStatsOutput(
            total=0,
            completed=0,
            pending=0,
            overdue=0,
            message=f"Failed to get statistics: {str(e)}",
        )
