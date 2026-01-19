# Production-Grade Multi-Agent Architecture Plan

**Feature**: AI Agent Chatbot for Todo Management
**Date**: 2026-01-15
**Reference**: This document provides the detailed multi-agent system design using OpenAI Agents SDK

---

## 1. Scope & Assumptions

### In Scope
- Backend: Multi-agent system using OpenAI Agents SDK with handoffs, tools, guardrails, sessions
- Backend: Function tools that call existing Todo CRUD APIs (no new API logic, just agent wrappers)
- Backend: Chat API endpoints (POST /api/v1/chat/message, GET /api/v1/chat/stream)
- Frontend: Chat UI accessible only on /dashboard for authenticated users
- Frontend: Real-time streaming of agent responses
- Security: User-scoped operations enforced in guardrails and tools
- Error handling: Graceful failures with user-friendly messages

### Out of Scope (Per User Request or V1 Limitation)
- MCP server creation (explicitly deferred to later phase)
- Persistent chat history across sessions
- Voice input/output
- Multi-language support beyond English
- External calendar integrations

### Assumptions
- Existing todo CRUD APIs (/api/v1/todos) are fully functional and authenticated
- User authentication middleware provides user_id from request context
- Dashboard route (/dashboard) already exists and is auth-protected
- OPENAI_API_KEY is available in environment variables
- SQLite is acceptable for session storage

---

## 2. Agent Inventory

### TodoManagerAgent (Primary/Triage Agent)
**Role**: Triage and route requests; handle todo CRUD operations

**Responsibilities**:
- Parse natural language commands related to todo management
- Create, update, delete, and query todos via function tools
- Ask clarifying questions when user input is ambiguous
- Confirm destructive operations (delete) before execution
- Hand off to AnalyticsAgent for complex queries/reports

**Inputs**: User message (string), session context (previous conversation)

**Outputs**: Natural language response + structured tool call results (JSON)

**Tools**: create_todo, get_todos, update_todo, delete_todo, search_todos

**Instructions**:
```
You are a helpful Todo Management Assistant. Your job is to help users manage their todo list through natural conversation.

When users ask to create todos, extract:
- Title (required)
- Description (optional)
- Due date (parse natural language dates like "tomorrow", "next Friday", "in 3 days")
- Priority (low/medium/high, default to medium if not specified)

For updates and deletes, identify the correct todo by matching keywords from the user's message to todo titles.

If the request is ambiguous, ask ONE clarifying question at a time. Be concise and friendly.

For complex analytics questions (e.g., "What's due this week?", "Show overdue tasks"), hand off to the AnalyticsAgent.

Always confirm successful operations to the user.
```

### AnalyticsAgent (Specialist Agent)
**Role**: Handle complex queries, filtering, and todo analytics

**Responsibilities**:
- Process queries about todo lists ("What's due today?", "Show overdue tasks")
- Filter todos by status, date ranges, priority
- Generate summary reports ("You have 3 overdue tasks")
- Return control to TodoManagerAgent after answering

**Inputs**: User query (string), session context

**Outputs**: Natural language analysis + filtered todo lists (JSON)

**Tools**: filter_todos_by_date, filter_todos_by_status, get_todo_statistics

**Instructions**:
```
You are a Todo Analytics Specialist. When users ask questions about their todos, provide clear, data-driven answers.

For date-based queries ("today", "this week", "overdue"), use the filter_todos_by_date tool with the appropriate filter type.

For status queries ("completed", "pending"), use filter_todos_by_status.

For summary questions ("how many tasks do I have?"), use get_todo_statistics.

Present results in a friendly, conversational way. For lists, format them clearly with bullets or numbers.

After answering, return control to the TodoManagerAgent if the user has follow-up actions (like creating or updating todos).
```

### Routing & Handoffs

```
User Message → TodoManagerAgent (Triage)
                    ↓
         ┌──────────┴──────────┐
         ↓                     ↓
   Standard CRUD         Complex Query?
   (TodoManagerAgent)    → handoff(AnalyticsAgent)
                              ↓
                         AnalyticsAgent processes
                              ↓
                         Return to TodoManagerAgent
                              ↓
                         Response to User
```

**Triage Policy** (implemented in TodoManagerAgent instructions):
- Commands with verbs "add", "create", "update", "delete", "mark" → TodoManagerAgent handles directly
- Questions with "what", "show", "how many", "which", date/time references → handoff to AnalyticsAgent
- Ambiguous requests → TodoManagerAgent asks clarifying questions first

**Escalation Rules**:
- If AnalyticsAgent cannot answer → return to TodoManagerAgent with message "I can only help with todo-related queries"
- If user authorization fails (guardrail triggers) → terminate with error message, no handoffs

---

## 3. Tools (Function Tools)

All tools are async functions decorated with @function_tool from the OpenAI Agents SDK.

### 3.1 create_todo
**Purpose**: Create a new todo for the authenticated user

**Schema**:
```python
class CreateTodoInput(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: Literal["low", "medium", "high"] = "medium"

class CreateTodoOutput(BaseModel):
    success: bool
    todo_id: int | None
    message: str
```

**Implementation**:
```python
@function_tool
async def create_todo(ctx: RunContextWrapper, input: CreateTodoInput) -> CreateTodoOutput:
    user_id = ctx.get("user_id")
    try:
        todo = await todo_service.create(
            user_id=user_id,
            title=input.title,
            description=input.description,
            due_date=input.due_date,
            priority=input.priority
        )
        return CreateTodoOutput(
            success=True,
            todo_id=todo.id,
            message=f"Created todo: {todo.title}"
        )
    except Exception as e:
        return CreateTodoOutput(
            success=False,
            message=f"Failed to create todo: {str(e)}"
        )
```

**Side Effects**: Inserts row in todos table via todo_service.create()

**Error Modes**:
- Validation failure (invalid date format) → return success=False, message="Invalid date"
- Database error → exception caught, returned in message field

### 3.2 get_todos
**Purpose**: Retrieve all todos for authenticated user

**Schema**:
```python
class GetTodosOutput(BaseModel):
    success: bool
    todos: list[TodoSchema]  # Reuses existing Pydantic schema
    message: str
```

**Implementation**:
```python
@function_tool
async def get_todos(ctx: RunContextWrapper) -> GetTodosOutput:
    user_id = ctx.get("user_id")
    try:
        todos = await todo_service.get_all(user_id=user_id)
        return GetTodosOutput(
            success=True,
            todos=todos,
            message=f"Retrieved {len(todos)} todos"
        )
    except Exception as e:
        return GetTodosOutput(
            success=False,
            todos=[],
            message=f"Failed to retrieve todos: {str(e)}"
        )
```

**Side Effects**: Read-only query

**Error Modes**: Database unavailable → empty list + error message

### 3.3 update_todo
**Purpose**: Update existing todo

**Schema**:
```python
class UpdateTodoInput(BaseModel):
    todo_id: int
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    status: Literal["pending", "completed"] | None = None
    priority: Literal["low", "medium", "high"] | None = None

class UpdateTodoOutput(BaseModel):
    success: bool
    message: str
```

**Implementation**: Similar pattern to create_todo, calls todo_service.update()

**Side Effects**: Updates row in todos table

**Error Modes**:
- Todo not found → success=False, message="Todo not found"
- Todo belongs to different user → caught by guardrail (see section 5)

### 3.4 delete_todo
**Purpose**: Delete a todo

**Schema**:
```python
class DeleteTodoInput(BaseModel):
    todo_id: int

class DeleteTodoOutput(BaseModel):
    success: bool
    message: str
```

**Implementation**:
```python
@function_tool
async def delete_todo(ctx: RunContextWrapper, input: DeleteTodoInput) -> DeleteTodoOutput:
    user_id = ctx.get("user_id")
    try:
        # Verify ownership before delete
        todo = await todo_service.get_by_id(input.todo_id, user_id=user_id)
        if not todo:
            return DeleteTodoOutput(success=False, message="Todo not found or access denied")

        await todo_service.delete(input.todo_id, user_id=user_id)
        return DeleteTodoOutput(success=True, message=f"Deleted todo: {todo.title}")
    except Exception as e:
        return DeleteTodoOutput(success=False, message=f"Failed to delete todo: {str(e)}")
```

**Side Effects**: Deletes row from todos table

**Error Modes**: Todo not found or unauthorized → success=False

### 3.5 search_todos
**Purpose**: Search todos by keywords

**Schema**:
```python
class SearchTodosInput(BaseModel):
    query: str

class SearchTodosOutput(BaseModel):
    success: bool
    todos: list[TodoSchema]
    message: str
```

**Implementation**: Calls todo_service with LIKE query on title/description

**Side Effects**: Read-only query

**Error Modes**: Empty results → return empty list (not an error)

### 3.6 filter_todos_by_date (AnalyticsAgent tool)
**Purpose**: Filter todos by date range

**Schema**:
```python
class FilterByDateInput(BaseModel):
    filter_type: Literal["today", "tomorrow", "this_week", "overdue"]

class FilterByDateOutput(BaseModel):
    success: bool
    todos: list[TodoSchema]
    count: int
    message: str
```

**Implementation**:
```python
@function_tool
async def filter_todos_by_date(ctx: RunContextWrapper, input: FilterByDateInput) -> FilterByDateOutput:
    user_id = ctx.get("user_id")
    now = datetime.now()

    if input.filter_type == "today":
        start = now.replace(hour=0, minute=0, second=0)
        end = now.replace(hour=23, minute=59, second=59)
    elif input.filter_type == "tomorrow":
        tomorrow = now + timedelta(days=1)
        start = tomorrow.replace(hour=0, minute=0, second=0)
        end = tomorrow.replace(hour=23, minute=59, second=59)
    elif input.filter_type == "this_week":
        start = now - timedelta(days=now.weekday())
        end = start + timedelta(days=6)
    elif input.filter_type == "overdue":
        todos = await todo_service.get_overdue(user_id=user_id)
        return FilterByDateOutput(
            success=True,
            todos=todos,
            count=len(todos),
            message=f"Found {len(todos)} overdue tasks"
        )

    todos = await todo_service.get_by_date_range(user_id=user_id, start=start, end=end)
    return FilterByDateOutput(
        success=True,
        todos=todos,
        count=len(todos),
        message=f"Found {len(todos)} todos for {input.filter_type}"
    )
```

**Side Effects**: Read-only query

**Error Modes**: None (empty results are valid)

### 3.7 filter_todos_by_status (AnalyticsAgent tool)
**Purpose**: Filter by status

**Schema**:
```python
class FilterByStatusInput(BaseModel):
    status: Literal["pending", "completed"]

class FilterByStatusOutput(BaseModel):
    success: bool
    todos: list[TodoSchema]
    count: int
    message: str
```

**Implementation**: Similar to filter_by_date, calls todo_service.get_by_status()

### 3.8 get_todo_statistics (AnalyticsAgent tool)
**Purpose**: Get summary stats

**Schema**:
```python
class TodoStatsOutput(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
    message: str
```

**Implementation**:
```python
@function_tool
async def get_todo_statistics(ctx: RunContextWrapper) -> TodoStatsOutput:
    user_id = ctx.get("user_id")
    all_todos = await todo_service.get_all(user_id=user_id)
    completed = [t for t in all_todos if t.status == "completed"]
    pending = [t for t in all_todos if t.status == "pending"]
    overdue = [t for t in pending if t.due_date and t.due_date < datetime.now()]

    return TodoStatsOutput(
        total=len(all_todos),
        completed=len(completed),
        pending=len(pending),
        overdue=len(overdue),
        message=f"Total: {len(all_todos)}, Completed: {len(completed)}, Pending: {len(pending)}, Overdue: {len(overdue)}"
    )
```

**Side Effects**: Read-only aggregation

**Error Modes**: None

---

## 4. Context Strategy

### What Persists
- **Conversation history**: Messages exchanged in current session (stored in SQLiteSession)
- **User context**: user_id extracted from authentication token, passed to all tools via ctx
- **Agent state**: Current active agent (TodoManager vs Analytics) tracked by SDK

### Session Keys
- **Format**: `user_{user_id}_session_{session_id}` where session_id is UUID generated on first message
- **Storage**: SQLite database at `.agent-sessions/conversations.db`
- **Retention**: Sessions expire after 24 hours of inactivity (cleanup job runs daily)

### Implementation
```python
from agents import SQLiteSession

async def get_session(user_id: str, session_id: str | None = None) -> SQLiteSession:
    if not session_id:
        session_id = str(uuid.uuid4())

    session_key = f"user_{user_id}_session_{session_id}"
    session = SQLiteSession(
        session_key,
        db_path=".agent-sessions/conversations.db"
    )
    return session, session_id
```

### What's Excluded
- No global context (agents cannot see other users' conversations)
- No persistent memory across browser sessions initially (session_id not stored in frontend)
- No long-term user preferences (future enhancement)

---

## 5. Guardrails

### 5.1 Input Guardrails

#### user_authorization_guardrail
**Purpose**: Ensure user is authenticated

**Implementation**:
```python
from agents import InputGuardrail, GuardrailFunctionOutput
from agents.exceptions import InputGuardrailTripwireTriggered

async def user_authorization_guardrail(ctx, agent, input_data):
    user_id = ctx.get("user_id")
    if not user_id:
        return GuardrailFunctionOutput(
            output_info="User not authenticated",
            tripwire_triggered=True
        )
    return GuardrailFunctionOutput(tripwire_triggered=False)
```

**Tripwire Policy**: Block all messages from unauthenticated users

**Remediation**: API endpoint returns 401 error

#### input_sanitization_guardrail
**Purpose**: Validate and sanitize user input

**Implementation**:
```python
async def input_sanitization_guardrail(ctx, agent, input_data):
    message = input_data.get("content", "")

    # Max length check
    if len(message) > 2000:
        return GuardrailFunctionOutput(
            output_info="Message too long (max 2000 characters)",
            tripwire_triggered=True
        )

    # Empty message check
    if not message or message.strip() == "":
        return GuardrailFunctionOutput(
            output_info="Empty message",
            tripwire_triggered=True
        )

    return GuardrailFunctionOutput(tripwire_triggered=False)
```

**Tripwire Policy**: Reject invalid inputs

**Remediation**: Return error message "Invalid input format"

#### rate_limit_guardrail
**Purpose**: Prevent abuse (max 30 requests per minute per user)

**Implementation**:
```python
from collections import defaultdict
from datetime import datetime, timedelta

# In-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)

async def rate_limit_guardrail(ctx, agent, input_data):
    user_id = ctx.get("user_id")
    now = datetime.now()

    # Clean old requests
    request_counts[user_id] = [
        ts for ts in request_counts[user_id]
        if now - ts < timedelta(minutes=1)
    ]

    # Check limit
    if len(request_counts[user_id]) >= 30:
        return GuardrailFunctionOutput(
            output_info="Rate limit exceeded (30 req/min)",
            tripwire_triggered=True
        )

    # Record this request
    request_counts[user_id].append(now)
    return GuardrailFunctionOutput(tripwire_triggered=False)
```

**Tripwire Policy**: Block requests exceeding limit

**Remediation**: API endpoint returns 429 error

### 5.2 Output Guardrails

#### todo_ownership_guardrail
**Purpose**: Ensure agent never returns todos belonging to other users

**Implementation**:
```python
from agents import output_guardrail, OutputGuardrailTripwireTriggered

@output_guardrail
async def todo_ownership_guardrail(ctx, agent, output):
    user_id = ctx.get("user_id")

    # Check if output contains todos
    if hasattr(output, "todos"):
        for todo in output.todos:
            if todo.user_id != user_id:
                # Security violation detected!
                return GuardrailFunctionOutput(
                    output_info=f"Unauthorized access attempt: todo {todo.id} belongs to user {todo.user_id}, not {user_id}",
                    tripwire_triggered=True
                )

    return GuardrailFunctionOutput(tripwire_triggered=False)
```

**Tripwire Policy**: Halt response, log security violation

**Remediation**: Return generic error "Unable to process request", log incident

---

## 6. Structured Outputs

All agent outputs use Pydantic BaseModel with output_type parameter.

### ChatResponse (Main Output)
```python
class ChatResponse(BaseModel):
    message: str  # Natural language response to user
    action_performed: Literal["create", "read", "update", "delete", "query", "none"] | None
    todos_affected: list[int] | None  # IDs of todos created/modified
    clarification_needed: bool = False
    clarification_prompt: str | None = None
```

**Usage**:
```python
agent = Agent(
    name="TodoManagerAgent",
    instructions="...",
    output_type=ChatResponse
)
```

This ensures the agent always returns a JSON response with the exact schema, no hallucinated fields.

---

## 7. MCP Integration

**Deferred per user request.** Current implementation uses direct function tools.

When MCP is added in future phase:
- Convert function tools to MCP server tools
- Use MCPServerStreamableHttp to expose tools
- Add MCP server configuration to agent initialization
- Trust boundary: Validate all MCP tool outputs with guardrails

---

## 8. Observability

### Tracing
```python
import os
from agents import set_tracing_export_api_key

set_tracing_export_api_key(os.environ["OPENAI_API_KEY"])
```

**Trace key events**:
- Agent handoffs
- Tool calls (with inputs/outputs)
- Guardrail triggers
- Errors/exceptions

**Correlation ID**: session_id attached to all traces

### Logging
**Structured JSON logs** with fields:
- user_id
- session_id
- agent_name
- tool_name
- duration_ms
- success (bool)
- error (if any)

**Log levels**:
- INFO: Normal operations (tool calls, handoffs)
- WARNING: Guardrail triggers, clarification requests
- ERROR: Tool failures, exceptions

**Log destination**: stdout (captured by container orchestration)

### Metrics (Prometheus)
```python
from prometheus_client import Counter, Histogram

chat_requests_total = Counter('chat_requests_total', 'Total chat requests', ['user_id', 'agent'])
chat_response_duration = Histogram('chat_response_duration_seconds', 'Response time')
tool_call_duration = Histogram('tool_call_duration_seconds', 'Tool execution time', ['tool_name'])
guardrail_triggers = Counter('guardrail_triggers_total', 'Guardrail triggers', ['guardrail_type'])
```

---

## 9. Failure Handling

### SDK Exceptions
```python
from agents.exceptions import (
    MaxTurnsExceeded,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    ModelBehaviorError,
)

try:
    result = await Runner.run(agent, user_message, session=session, context={"user_id": user_id})
except MaxTurnsExceeded:
    return {"error": "Conversation too long, please start a new session"}
except InputGuardrailTripwireTriggered:
    return {"error": "Request blocked by security policy", "code": 403}
except OutputGuardrailTripwireTriggered:
    log_security_violation(user_id, session_id)
    return {"error": "Unable to process request", "code": 500}
except ModelBehaviorError:
    return {"error": "Agent encountered an error, please try again"}
except Exception as e:
    log_error(e)
    return {"error": "Unexpected error", "code": 500}
```

### Retries
- **Tool calls**: Retry up to 2 times on transient failures (network, timeout)
- **Agent execution**: No retries (user can resend message)
- **Database operations**: Use existing retry logic from todo_service

### Max Turns
- Set max_turns=10 per conversation to prevent infinite loops
- When exceeded, return error and suggest starting new session

### Fallbacks
- If AnalyticsAgent cannot answer → handoff back to TodoManagerAgent with explanation
- If all tools fail → agent returns apology message and suggests manual todo management
- If OpenAI API unavailable → return "Service temporarily unavailable" (no fallback model)

---

## 10. Test Plan

### Unit Tests (backend/app/tests/test_agents/)

#### test_tools.py
```python
import pytest
from app.agents.tools import create_todo, get_todos, update_todo, delete_todo
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_create_todo_success():
    # Mock context and todo_service
    ctx = MagicMock()
    ctx.get.return_value = "user123"

    with patch("app.agents.tools.todo_service") as mock_service:
        mock_service.create.return_value = MagicMock(id=1, title="Test task")

        input = CreateTodoInput(title="Test task", priority="high")
        result = await create_todo(ctx, input)

        assert result.success is True
        assert result.todo_id == 1
        assert "Test task" in result.message

@pytest.mark.asyncio
async def test_create_todo_unauthorized():
    # Test that tool fails if user_id is None
    ctx = MagicMock()
    ctx.get.return_value = None

    # Should be caught by guardrail before reaching tool
    # But tool should handle gracefully anyway
    ...

# Similar tests for all 8 tools
```

#### test_guardrails.py
```python
import pytest
from app.agents.guardrails import (
    user_authorization_guardrail,
    input_sanitization_guardrail,
    todo_ownership_guardrail
)

@pytest.mark.asyncio
async def test_user_authorization_blocks_unauthenticated():
    ctx = MagicMock()
    ctx.get.return_value = None  # No user_id

    result = await user_authorization_guardrail(ctx, None, {})

    assert result.tripwire_triggered is True
    assert "not authenticated" in result.output_info.lower()

@pytest.mark.asyncio
async def test_input_sanitization_blocks_too_long():
    ctx = MagicMock()
    long_message = "x" * 2001

    result = await input_sanitization_guardrail(ctx, None, {"content": long_message})

    assert result.tripwire_triggered is True

@pytest.mark.asyncio
async def test_todo_ownership_blocks_other_user_todos():
    ctx = MagicMock()
    ctx.get.return_value = "user123"

    # Create output with todo belonging to different user
    output = MagicMock()
    todo = MagicMock()
    todo.user_id = "user456"
    todo.id = 99
    output.todos = [todo]

    result = await todo_ownership_guardrail(ctx, None, output)

    assert result.tripwire_triggered is True
```

#### test_agents.py
```python
import pytest
from app.agents.agents import todo_manager_agent, analytics_agent

@pytest.mark.asyncio
async def test_todo_manager_handles_create_command():
    # Mock Runner.run
    with patch("app.agents.agents.Runner") as mock_runner:
        mock_runner.run.return_value = MagicMock(
            final_output=ChatResponse(
                message="Created task: Buy milk",
                action_performed="create",
                todos_affected=[1]
            )
        )

        result = await mock_runner.run(
            todo_manager_agent,
            "Add a task to buy milk",
            context={"user_id": "user123"}
        )

        assert result.final_output.action_performed == "create"
        assert "Buy milk" in result.final_output.message

@pytest.mark.asyncio
async def test_handoff_to_analytics_agent():
    # Test that TodoManager hands off to Analytics for query
    # Verify handoff occurs when user asks "What's due today?"
    ...
```

### Integration Tests (backend/app/tests/test_chat_api.py)

```python
import pytest
from fastapi.testclient import TestClient

def test_chat_endpoint_requires_auth(client: TestClient):
    response = client.post("/api/v1/chat/message", json={"message": "Hello"})
    assert response.status_code == 401

def test_chat_endpoint_creates_todo(client: TestClient, auth_headers):
    response = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={"message": "Add a task to test the API"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["action_performed"] == "create"
    assert "test the API" in data["message"].lower()

def test_chat_session_continuity(client: TestClient, auth_headers):
    # Send first message
    response1 = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={"message": "Add a task called Testing"}
    )
    session_id = response1.json().get("session_id")

    # Send follow-up message referencing previous context
    response2 = client.post(
        "/api/v1/chat/message",
        headers=auth_headers,
        json={"message": "Mark it as high priority", "session_id": session_id}
    )
    assert response2.status_code == 200
    # Agent should understand "it" refers to "Testing" task
```

### Smoke Test (scripts/smoke_test.py)

```python
#!/usr/bin/env python3
import asyncio
import httpx

async def smoke_test():
    base_url = "http://localhost:8000/api/v1"

    # 1. Authenticate
    auth_response = await httpx.post(f"{base_url}/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create todo via chat
    print("Test 1: Create todo...")
    response = await httpx.post(
        f"{base_url}/chat/message",
        headers=headers,
        json={"message": "Add a task to test the chatbot"}
    )
    assert response.status_code == 200
    assert response.json()["action_performed"] == "create"
    print("✓ Create todo passed")

    # 3. Query todos
    print("Test 2: Query todos...")
    response = await httpx.post(
        f"{base_url}/chat/message",
        headers=headers,
        json={"message": "What are my pending tasks?"}
    )
    assert response.status_code == 200
    assert "test the chatbot" in response.json()["message"].lower()
    print("✓ Query todos passed")

    # 4. Delete todo
    print("Test 3: Delete todo...")
    response = await httpx.post(
        f"{base_url}/chat/message",
        headers=headers,
        json={"message": "Delete the test task"}
    )
    assert response.status_code == 200
    print("✓ Delete todo passed")

    print("\n✅ All smoke tests passed!")

if __name__ == "__main__":
    asyncio.run(smoke_test())
```

**Run**: `python scripts/smoke_test.py`

---

## 11. Deployment Checklist

### Prerequisites
- [ ] OPENAI_API_KEY environment variable set
- [ ] Python 3.13+ installed
- [ ] Backend dependencies installed: `uv add openai-agents`

### Backend
- [ ] Create `.agent-sessions/` directory
- [ ] Add `.agent-sessions/` to `.gitignore`
- [ ] Deploy updated backend with `/api/v1/chat` endpoints
- [ ] Verify health check: `curl http://localhost:8000/api/v1/health`

### Frontend
- [ ] Build and deploy frontend with chat UI components
- [ ] Verify `/dashboard` renders chat interface
- [ ] Test authentication (unauthenticated users see login prompt)

### Testing
- [ ] Run unit tests: `pytest backend/app/tests/test_agents/`
- [ ] Run integration tests: `pytest backend/app/tests/test_chat_api.py`
- [ ] Run smoke test: `python scripts/smoke_test.py`

### Monitoring
- [ ] Confirm traces appear in OpenAI dashboard (if tracing enabled)
- [ ] Set up alerts for high error rates (>5%)
- [ ] Set up alerts for guardrail trigger spikes

---

## 12. Acceptance Criteria

### Backend
- ✅ TodoManagerAgent and AnalyticsAgent implemented with handoffs
- ✅ 8 function tools implemented with Pydantic schemas
- ✅ Input guardrails (auth, sanitization, rate limit) functional
- ✅ Output guardrail (todo ownership) functional
- ✅ SQLite session management configured
- ✅ Chat API endpoints (/api/v1/chat/message) functional
- ✅ All unit tests pass
- ✅ Smoke test completes successfully

### Frontend
- ✅ Chat UI accessible on /dashboard for authenticated users
- ✅ Real-time agent responses displayed
- ✅ User can send messages and receive responses in <3s (95% of requests)
- ✅ Error messages displayed gracefully
- ✅ UI responsive on mobile and desktop

### Security
- ✅ Unauthenticated users cannot access chat (401 error)
- ✅ Agent never accesses other users' todos (guardrail blocks)
- ✅ Rate limiting prevents abuse (30 req/min per user)

### Performance
- ✅ Agent response time <3s for 95% of requests
- ✅ Natural language command accuracy ≥90%
- ✅ Tool call success rate ≥95%

---

**Next Steps**: Phase 0 (Research), Phase 1 (Design), Phase 2 (Tasks), Phase 3 (Implementation)
