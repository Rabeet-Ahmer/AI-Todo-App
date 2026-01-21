# Implementation Plan: AI Agent Chatbot for Todo Management (Simplified v2)

**Branch**: `001-agent-chatbot` | **Date**: 2026-01-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-agent-chatbot/spec.md`

## Summary

This feature adds a **simple AI-powered chatbot** to the Todo Web App for natural language todo management. The chatbot is accessible only on `/dashboard` for authenticated users. It uses **OpenAI Agents SDK (Python)** with a single TodoAgent that has function tools calling **existing TodoService** directly (reusing existing Pydantic models, auth patterns, and business logic).

**Simplified Approach**:
- ✅ Single agent (TodoAgent) - no multi-agent handoffs
- ✅ Tools call `TodoService` directly (same pattern as `todos.py` router)
- ✅ Reuse existing `TodoCreate`, `TodoUpdate`, `TodoResponse`, `TodoStats` schemas
- ✅ Reuse existing `get_current_user`, `get_session` dependencies
- ✅ All agent endpoints in single `chat.py` file
- ✅ SQLite sessions for conversation history (agent remembers context)
- ✅ Floating chat button → opens modal/drawer
- ✅ Casual agent tone ("Done! Added to your list")
- ✅ User-friendly error messages
- ❌ No guardrails (future enhancement)
- ❌ No streaming responses (simple request/response)
- ❌ No multi-agent orchestration

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: `openai-agents`, FastAPI 0.128+, Pydantic v2, SQLModel, Neon PostgreSQL
- Frontend: Next.js 16.1.1, React 19.2.3, TailwindCSS 4.x
**Storage**: Neon PostgreSQL (existing) + SQLite for agent conversation sessions
**Target Platform**: FastAPI service (backend), Next.js web app (frontend)

**Performance Goals**:
- Agent response time: <5s for 95% of requests
- Natural language command accuracy: 80%+

**Constraints**:
- Auth-only access (reuses existing `get_current_user` dependency)
- User-scoped operations (TodoService already enforces this)
- Session-based chat (SQLite stores conversation history per user)
- Sessions auto-expire after 24 hours of inactivity

**Scale/Scope**:
- 1 agent (TodoAgent)
- 5 function tools (create, list, update, delete, stats)
- ~200-300 lines of agent code
- Frontend: 4-5 React components for chat UI

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│           Frontend (Next.js)                    │
│  FloatingChatButton → ChatDrawer → ChatWindow   │
└─────────────────────────────────────────────────┘
                     │ POST /api/v1/chat/message
                     │ (with session_id cookie/header)
                     ▼
┌─────────────────────────────────────────────────┐
│           chat.py (FastAPI Router)              │
│  - Authenticates via get_current_user           │
│  - Loads/creates SQLite session for user        │
│  - Runs agent with Runner.run() + session       │
└─────────────────────────────────────────────────┘
                     │
          ┌─────────┴─────────┐
          ▼                   ▼
┌──────────────────┐  ┌──────────────────┐
│  SQLite Sessions │  │   TodoAgent      │
│  - Conversation  │  │  - NL parsing    │
│    history       │  │  - 5 tools       │
│  - Per user_id   │  └──────────────────┘
└──────────────────┘          │ function_tool calls
                              ▼
              ┌─────────────────────────────────┐
              │       TodoService (existing)    │
              │  - create_todo, get_todos, etc. │
              └─────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │ PostgreSQL   │
                    │ (Neon)       │
                    └──────────────┘
```

## Key Design Decisions

### 1. Tools Call TodoService Directly

Agent tools will follow the **exact same pattern** as `todos.py` router:

```python
# Existing pattern in todos.py:
@router.post("", response_model=TodoResponse)
async def create_todo(
    todo_in: TodoCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    return await TodoService.create_todo(session, todo_in, current_user.id)

# Agent tool will do the same (session & user_id passed via RunContext):
@function_tool
async def create_todo(ctx: RunContext[AgentContext], title: str, ...):
    session = ctx.context.session
    user_id = ctx.context.user_id
    todo_in = TodoCreate(title=title, ...)
    return await TodoService.create_todo(session, todo_in, user_id)
```

### 2. Reuse Existing Pydantic Schemas

- `TodoCreate` - for create_todo tool input
- `TodoUpdate` - for update_todo tool input
- `TodoResponse` - for tool outputs (agent sees the response)
- `TodoStats` - for stats tool output

### 3. Authentication via Existing Dependency

```python
# chat.py uses same auth as todos.py:
@router.post("/message")
async def chat_message(
    message: ChatRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    # Pass user_id and session to agent context
    context = AgentContext(user_id=current_user.id, session=session)
    result = await Runner.run(todo_agent, message.content, context=context)
    return ChatResponse(message=result.final_output)
```

### 4. Single File Backend Structure

All agent code in `chat.py`:
- `AgentContext` dataclass
- Tool definitions (`@function_tool`)
- `todo_agent` definition
- SQLite session management functions
- Chat router endpoints

### 5. SQLite Session Management

```python
# Sessions stored in backend/.agent-sessions/sessions.db
# Table: chat_sessions
#   - user_id (str, primary key)
#   - session_data (JSON blob - OpenAI Agents SDK format)
#   - created_at (datetime)
#   - updated_at (datetime)

# Session lifecycle:
# 1. On first message: create new session for user_id
# 2. On subsequent messages: load existing session, pass to Runner.run()
# 3. After agent response: save updated session
# 4. Auto-cleanup: delete sessions older than 24 hours
```

### 6. Floating Chat UI (Frontend)

```
frontend/components/chat/
├── ChatButton.tsx      # Floating button (bottom-right corner)
├── ChatDrawer.tsx      # Drawer/modal container (slides in from right)
├── ChatWindow.tsx      # Main chat content (messages + input)
├── ChatMessage.tsx     # Individual message bubble
├── ChatInput.tsx       # Input field with send button
└── ChatLoading.tsx     # Loading indicator
```

**UI Flow**:
1. User clicks floating button → ChatDrawer opens
2. ChatDrawer contains ChatWindow
3. User can minimize/close drawer
4. Badge on button shows unread messages (optional)

## Project Structure (Simplified)

### Backend Changes

```
backend/
├── app/
│   ├── api/v1/
│   │   ├── chat.py         # NEW - All agent logic + endpoints + session mgmt
│   │   └── router.py       # UPDATE - Include chat router
│   ├── schemas/
│   │   └── chat.py         # NEW - ChatRequest, ChatResponse
│   └── services/
│       └── todo_service.py # EXISTING - No changes
├── .agent-sessions/        # NEW (gitignored) - SQLite session storage
│   └── sessions.db
└── pyproject.toml          # UPDATE - Add openai-agents
```

### Frontend Changes

```
frontend/
├── app/dashboard/
│   └── layout.tsx          # UPDATE - Add ChatButton (floating)
├── components/chat/        # NEW
│   ├── ChatButton.tsx      # Floating button component
│   ├── ChatDrawer.tsx      # Drawer container
│   ├── ChatWindow.tsx      # Chat content
│   ├── ChatMessage.tsx     # Message bubble
│   ├── ChatInput.tsx       # Input field
│   └── ChatLoading.tsx     # Loading indicator
├── lib/
│   ├── api-client.ts       # UPDATE - Add chat API method
│   └── types.ts            # UPDATE - Add chat types
└── hooks/
    └── use-chat.ts         # NEW - Chat state management
```

## API Contract

### POST /api/v1/chat/message

**Request**:
```json
{
  "content": "Create a todo to buy groceries"
}
```

**Response**:
```json
{
  "message": "I've created a new todo 'Buy groceries' with medium priority.",
  "todos_affected": [
    {
      "id": 123,
      "title": "Buy groceries",
      "completed": false,
      "priority": "MEDIUM"
    }
  ]
}
```

**Error Response** (401/500):
```json
{
  "detail": "Error message here"
}
```

## Agent Tools Specification

### 1. create_todo
- **Input**: title (str), description (str, optional), priority (str, default "MEDIUM")
- **Output**: Created todo details
- **Calls**: `TodoService.create_todo()`

### 2. list_todos
- **Input**: None
- **Output**: List of user's todos
- **Calls**: `TodoService.get_todos()`

### 3. update_todo
- **Input**: todo_id (int), title (str, optional), description (str, optional), completed (bool, optional), priority (str, optional)
- **Output**: Updated todo details
- **Calls**: `TodoService.update_todo()`

### 4. delete_todo
- **Input**: todo_id (int)
- **Output**: Confirmation message
- **Calls**: `TodoService.delete_todo()`

### 5. get_stats
- **Input**: None
- **Output**: TodoStats (total, pending, completed)
- **Calls**: `TodoService.get_stats()`

## Agent Instructions

```python
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
```

## Constitution Check (Simplified)

### ✅ Passes

1. **Component-First (I)**: Small, focused chat components
2. **Type Safety (II)**: Reuses existing Pydantic schemas; TypeScript for frontend
3. **Server-Client Clarity (III)**: ChatWindow is Client Component for interactivity
4. **Predictable Data Flow (IV)**: Props down, events up; clear API contract
5. **Styling as System (V)**: TailwindCSS only
6. **API-First (VI)**: Clear POST /chat/message contract
7. **Performance-Aware (VII)**: Simple request/response, no streaming overhead
8. **Tooling by Necessity (VIII)**: Only openai-agents added (required)
9. **Explicit Data Modeling (IX)**: Reuses existing TodoService patterns
10. **Error Handling (X)**: Existing exception handlers apply

### ⚠️ Requires Justification

- **New dependency**: `openai-agents` - JUSTIFIED (core feature requirement)

---

**Plan Status**: ✅ Simplified v2 Ready for Implementation
**Plan Date**: 2026-01-21
**Approved By**: Pending user review

