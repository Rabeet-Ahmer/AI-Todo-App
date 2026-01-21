---
description: "Simplified implementation tasks for AI Agent Chatbot feature (v2.1)"
---

# Tasks: AI Agent Chatbot for Todo Management (Simplified v2.1)

**Input**: Simplified plan from `/specs/001-agent-chatbot/plan.md`
**Prerequisites**: plan.md, spec.md

**Key Updates in v2.1**:
- ✅ SQLite sessions for conversation history
- ✅ Floating chat button with drawer UI
- ✅ Casual agent tone
- ✅ User-friendly error messages

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for application code
- **Frontend**: `frontend/` for Next.js application

---

## Phase 1: Setup & Dependencies

**Purpose**: Install openai-agents and configure environment

- [ ] T001 Install openai-agents package: `uv add openai-agents` in backend/
- [ ] T002 [P] Add OPENAI_API_KEY to backend/.env (required for agents SDK)
- [ ] T003 [P] Create `backend/.agent-sessions/` directory for SQLite storage
- [ ] T004 [P] Add `.agent-sessions/` to `backend/.gitignore`

---

## Phase 2: Backend - Chat Schemas

**Purpose**: Create Pydantic schemas for chat API

- [ ] T005 Create `backend/app/schemas/chat.py` with:
  - `ChatRequest(BaseModel)`: content (str)
  - `ChatResponse(BaseModel)`: message (str), todos_affected (list[TodoResponse], optional)
  - `ChatHistoryItem(BaseModel)`: role (str), content (str), timestamp (datetime)

---

## Phase 3: Backend - SQLite Session Management

**Purpose**: Session storage for conversation history (in chat.py)

**Dependencies**: T003

- [ ] T006 Create SQLite session functions in `backend/app/api/v1/chat.py`:
  - `init_session_db()`: Create sessions.db and table if not exists
  - Table schema: `user_id TEXT PRIMARY KEY, session_data TEXT, created_at TEXT, updated_at TEXT`

- [ ] T007 [P] Implement `get_user_session(user_id: str)` function:
  - Returns existing session data (JSON) or None
  - Query: `SELECT session_data FROM chat_sessions WHERE user_id = ?`

- [ ] T008 [P] Implement `save_user_session(user_id: str, session_data: str)` function:
  - Upsert session data (INSERT OR REPLACE)
  - Update `updated_at` timestamp

- [ ] T009 [P] Implement `clear_user_session(user_id: str)` function:
  - Delete session for user (for "clear chat" feature)

- [ ] T010 Add session cleanup (delete sessions older than 24 hours):
  - Can be called on app startup or as background task
  - Query: `DELETE FROM chat_sessions WHERE updated_at < datetime('now', '-24 hours')`

---

## Phase 4: Backend - Agent & Tools in chat.py

**Purpose**: All agent logic in single chat.py file, reusing TodoService

**Dependencies**: T001, T005, T006

### Agent Context & Tools

- [ ] T011 Add imports to `backend/app/api/v1/chat.py`:
  - `from agents import Agent, Runner, function_tool, RunContext`
  - `from app.services.todo_service import TodoService`
  - `from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse, TodoStats`
  - `from app.api.deps import get_current_user, get_session`

- [ ] T012 Define `AgentContext` dataclass in chat.py:
  ```python
  @dataclass
  class AgentContext:
      user_id: str
      session: AsyncSession  # PostgreSQL session for TodoService
  ```

- [ ] T013 Implement `create_todo` function tool in chat.py:
  - Inputs: title (str), description (str, optional), priority (str, default "MEDIUM")
  - Uses `ctx.context.session` and `ctx.context.user_id`
  - Calls `TodoService.create_todo(session, TodoCreate(...), user_id)`
  - Returns todo dict for agent

- [ ] T014 [P] Implement `list_todos` function tool in chat.py:
  - No inputs
  - Calls `TodoService.get_todos(session, user_id)`
  - Returns list of todo dicts

- [ ] T015 [P] Implement `update_todo` function tool in chat.py:
  - Inputs: todo_id (int), title (str, optional), description (str, optional), completed (bool, optional), priority (str, optional)
  - Calls `TodoService.update_todo(session, todo_id, TodoUpdate(...), user_id)`
  - Returns updated todo dict

- [ ] T016 [P] Implement `delete_todo` function tool in chat.py:
  - Input: todo_id (int)
  - Calls `TodoService.delete_todo(session, todo_id, user_id)`
  - Returns confirmation message

- [ ] T017 [P] Implement `get_stats` function tool in chat.py:
  - No inputs
  - Calls `TodoService.get_stats(session, user_id)`
  - Returns stats dict (total, pending, completed)

### Agent Definition

- [ ] T018 Define `todo_agent` in chat.py:
  - Name: "TodoAgent"
  - Instructions: Casual tone instructions (see plan.md for full text)
  - Tools: [create_todo, list_todos, update_todo, delete_todo, get_stats]
  - Model: "gpt-4o-mini" (cost-effective)

### Chat Router Endpoints

- [ ] T019 Create FastAPI router in chat.py:
  - `router = APIRouter(prefix="/chat", tags=["chat"])`
  - Call `init_session_db()` at module level

- [ ] T020 Implement `POST /chat/message` endpoint:
  - Request body: ChatRequest
  - Dependencies: get_current_user, get_session (PostgreSQL)
  - Load SQLite session: `session_data = get_user_session(current_user.id)`
  - Create AgentContext with user_id and session
  - Run agent with session: `result = await Runner.run(todo_agent, message.content, context=context)`
  - Save updated session: `save_user_session(current_user.id, result.session_data)`
  - Return ChatResponse with result.final_output

- [ ] T021 Add user-friendly error handling in chat endpoint:
  - Catch agent exceptions → "Sorry, I couldn't complete that. Please try again."
  - Catch TodoNotFoundException → "Hmm, I couldn't find that todo. Want me to show your list?"
  - Log errors for debugging (don't expose to user)

- [ ] T022 [P] Implement `DELETE /chat/session` endpoint:
  - Clear chat history for current user
  - Call `clear_user_session(current_user.id)`
  - Return `{"message": "Chat history cleared"}`

### Router Registration

- [ ] T023 Update `backend/app/api/v1/router.py`:
  - Import chat router: `from app.api.v1 import chat`
  - Include router: `router.include_router(chat.router)`

---

## Phase 5: Frontend - Chat Types & API Client

**Purpose**: TypeScript types and API client for chat

- [ ] T024 Add chat types to `frontend/lib/types.ts`:
  ```typescript
  export interface ChatMessage {
    role: "user" | "assistant"
    content: string
    timestamp: Date
  }

  export interface ChatRequest {
    content: string
  }

  export interface ChatResponse {
    message: string
    todos_affected?: Todo[]
  }
  ```

- [ ] T025 Add chat API methods to `frontend/lib/api-client.ts`:
  ```typescript
  chat: {
    sendMessage: (content: string) => apiRequest<ChatResponse>("/chat/message", {
      method: "POST",
      body: JSON.stringify({ content })
    }),
    clearHistory: () => apiRequest<{message: string}>("/chat/session", {
      method: "DELETE"
    })
  }
  ```

---

## Phase 6: Frontend - Chat Components

**Purpose**: Create floating chat UI components

**Dependencies**: T024, T025

### Floating Button & Drawer

- [ ] T026 Create `frontend/components/chat/ChatButton.tsx`:
  - "use client" directive
  - Floating button fixed at bottom-right corner
  - Props: onClick (callback), isOpen (boolean)
  - Icon: chat bubble or message icon
  - Style: rounded, primary color, shadow
  - Animate on hover

- [ ] T027 Create `frontend/components/chat/ChatDrawer.tsx`:
  - "use client" directive
  - Props: isOpen (boolean), onClose (callback), children
  - Slides in from right side (or bottom on mobile)
  - Backdrop overlay (click to close)
  - Header with title "Chat Assistant" and close button
  - Use shadcn/ui Sheet component if available, or custom implementation

### Chat Content Components

- [ ] T028 [P] Create `frontend/components/chat/ChatMessage.tsx`:
  - Props: message (ChatMessage)
  - User messages: right-aligned, primary background
  - Assistant messages: left-aligned, secondary background
  - Show timestamp (optional, on hover)
  - Use TailwindCSS for styling

- [ ] T029 [P] Create `frontend/components/chat/ChatInput.tsx`:
  - Props: onSend (callback), disabled (boolean)
  - Text input with send button
  - Handle Enter key to send (Shift+Enter for newline)
  - Clear input after send
  - Disable while loading
  - Use TailwindCSS for styling

- [ ] T030 [P] Create `frontend/components/chat/ChatLoading.tsx`:
  - Animated dots or spinner
  - Text: "Thinking..."
  - Use TailwindCSS for styling

### Chat Window Container

- [ ] T031 Create `frontend/components/chat/ChatWindow.tsx`:
  - "use client" directive
  - Render: ChatMessage list, ChatLoading (when loading), ChatInput
  - Auto-scroll to bottom on new messages
  - Empty state: "Hi! I can help you manage your todos. Try saying 'show my todos' or 'add a task to buy groceries'"
  - "Clear chat" button in header (calls clearHistory API)

---

## Phase 7: Frontend - Chat Hook

**Purpose**: Custom hook for chat state management

**Dependencies**: T025, T031

- [ ] T032 Create `frontend/hooks/use-chat.ts`:
  - State: messages (ChatMessage[]), isLoading (boolean), error (string | null)
  - Function: `sendMessage(content: string)`:
    1. Add user message to state
    2. Set isLoading = true
    3. Call API
    4. Add assistant response to state
    5. Set isLoading = false
  - Function: `clearHistory()`:
    1. Call clearHistory API
    2. Reset messages to empty array
  - Handle API errors → set user-friendly error message
  - Return: { messages, isLoading, error, sendMessage, clearHistory }

- [ ] T033 Update ChatWindow.tsx to use useChat hook:
  - Replace any local state with hook
  - Connect ChatInput.onSend to sendMessage
  - Connect "Clear chat" to clearHistory
  - Display error message if present (toast or inline)

---

## Phase 8: Dashboard Integration

**Purpose**: Add floating chat to dashboard

**Dependencies**: T033

- [ ] T034 Create `frontend/components/chat/ChatContainer.tsx`:
  - "use client" directive
  - State: isOpen (boolean)
  - Render ChatButton + ChatDrawer + ChatWindow
  - Toggle isOpen on button click
  - This is the main component to import into dashboard

- [ ] T035 Update `frontend/app/dashboard/layout.tsx`:
  - Import ChatContainer component
  - Add ChatContainer at the end of layout (after children)
  - This makes chat available on all dashboard pages

- [ ] T036 [P] Create `frontend/components/chat/index.ts` barrel export:
  - Export ChatContainer as default
  - Export individual components for flexibility

---

## Phase 9: Testing & Verification

**Purpose**: Manual testing and verification

- [ ] T037 Test backend endpoint manually:
  - Start backend: `uv run uvicorn app.main:app --reload`
  - Test with curl (first message - creates session):
    ```bash
    curl -X POST http://localhost:8000/api/v1/chat/message \
      -H "Authorization: Bearer <jwt>" \
      -H "Content-Type: application/json" \
      -d '{"content": "Create a todo to test the chatbot"}'
    ```
  - Test with follow-up (uses existing session):
    ```bash
    curl -X POST http://localhost:8000/api/v1/chat/message \
      -H "Authorization: Bearer <jwt>" \
      -H "Content-Type: application/json" \
      -d '{"content": "Now mark it as complete"}'
    ```
  - Verify session persists (agent remembers previous message)

- [ ] T038 [P] Test frontend integration:
  - Start frontend: `npm run dev`
  - Log in and navigate to dashboard
  - Click floating chat button
  - Send message and verify response
  - Test conversation continuity (multiple messages)
  - Test "clear chat" button
  - Test closing and reopening drawer

- [ ] T039 Test edge cases:
  - Unauthenticated access (should fail with 401)
  - Empty message (should handle gracefully)
  - Very long message (should handle or truncate)
  - Rapid messages (should queue or handle)
  - Session expiry (after 24 hours)

---

## Dependencies & Execution Order

### Critical Path

```
T001 (install) → T003-T004 (setup) → T005 (schemas) → T006-T010 (SQLite) → T011-T018 (agent) → T019-T023 (router)
                                                                                                      ↓
T024-T025 (types/api) → T026-T031 (components) → T032-T033 (hook) → T034-T036 (integration)
```

### Parallel Opportunities

**Phase 1**: T002, T003, T004 can run in parallel
**Phase 3**: T007, T008, T009 can run in parallel (session functions)
**Phase 4**: T014, T015, T016, T017 can run in parallel (tools)
**Phase 6**: T028, T029, T030 can run in parallel (chat components)
**Phase 8**: T036 can run parallel to T035
**Phase 9**: T037, T038 can run in parallel

### Suggested Execution Groups

**Group 1 (Backend Setup)**:
- T001 → T002, T003, T004 (parallel)

**Group 2 (Backend Schemas & Sessions)**:
- T005 → T006 → T007, T008, T009 (parallel) → T010

**Group 3 (Backend Agent & Tools)**:
- T011 → T012 → T013, T014, T015, T016, T017 (parallel) → T018

**Group 4 (Backend Router)**:
- T019 → T020 → T021, T022 (parallel) → T023

**Group 5 (Frontend Foundation)**:
- T024 → T025

**Group 6 (Frontend Components)**:
- T026 → T027 (drawer depends on button design)
- T028, T029, T030 (parallel)
- T031 (after T028-T030)

**Group 7 (Frontend Integration)**:
- T032 → T033 → T034 → T035, T036 (parallel)

**Group 8 (Testing)**:
- T037, T038 (parallel) → T039

---

## Task Summary

**Total Tasks**: 39

**Breakdown by Phase**:
- Phase 1 (Setup): 4 tasks
- Phase 2 (Schemas): 1 task
- Phase 3 (SQLite Sessions): 5 tasks
- Phase 4 (Agent & Tools): 13 tasks
- Phase 5 (Types & API): 2 tasks
- Phase 6 (Components): 6 tasks
- Phase 7 (Hook): 2 tasks
- Phase 8 (Dashboard): 3 tasks
- Phase 9 (Testing): 3 tasks

**Parallel Opportunities**: 20 tasks can run in parallel within their phase

**Estimated Implementation**: ~300-400 lines backend, ~400-500 lines frontend

---

## Implementation Notes

### Backend Key Points

1. **All code in chat.py** - agent, tools, sessions, router
2. **SQLite for sessions** - separate from PostgreSQL (simpler, self-contained)
3. **Reuse TodoService** - same auth, same patterns
4. **User-friendly errors** - catch exceptions, return friendly messages
5. **Session cleanup** - auto-delete after 24 hours

### Frontend Key Points

1. **Floating button + drawer** - non-intrusive, always accessible
2. **ChatContainer** - single component to add to dashboard
3. **useChat hook** - all state logic in one place
4. **Auto-scroll** - always show latest message
5. **Clear chat** - user can reset conversation

### Testing Key Points

1. **JWT required** - get token from Better Auth first
2. **Test session persistence** - send multiple messages, verify context
3. **Check SQLite file** - `backend/.agent-sessions/sessions.db`
4. **Verify casual tone** - agent should respond friendly

---

**Tasks Status**: ✅ Ready for Implementation (v2.1)
**Tasks Date**: 2026-01-21
**Approved By**: Pending user review
