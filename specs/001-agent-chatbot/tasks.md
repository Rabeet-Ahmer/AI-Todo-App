---
description: "Implementation tasks for AI Agent Chatbot feature"
---

# Tasks: AI Agent Chatbot for Todo Management

**Input**: Design documents from `/specs/001-agent-chatbot/`
**Prerequisites**: plan.md, spec.md, agent-architecture-plan.md

**Tests**: Tests are NOT requested in the specification, so test tasks are excluded from this implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for application code
- **Frontend**: `frontend/` for Next.js application
- **Tests**: `backend/app/tests/` and `frontend/__tests__/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependencies for agent system

- [ ] T001 Install openai-agents package in backend: `uv add openai-agents` (or pip install openai-agents)
- [ ] T002 [P] Create `.agent-sessions/` directory in backend root for SQLite session storage
- [ ] T003 [P] Add `.agent-sessions/` to `.gitignore`
- [ ] T004 [P] Set OPENAI_API_KEY environment variable in backend/.env
- [ ] T005 [P] Update backend/pyproject.toml with openai-agents dependency if using uv

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core agent infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create backend/app/agents/ module directory structure with __init__.py
- [ ] T007 [P] Create backend/app/agents/config.py with agent configuration (model settings, API key loading)
- [ ] T008 [P] Create backend/app/agents/models.py with Pydantic base models for tool inputs/outputs
- [ ] T009 [P] Create backend/app/agents/sessions.py with SQLite session management functions
- [ ] T010 Create backend/app/agents/guardrails.py with user_authorization_guardrail function
- [ ] T011 [P] Add input_sanitization_guardrail to backend/app/agents/guardrails.py
- [ ] T012 [P] Add rate_limit_guardrail to backend/app/agents/guardrails.py
- [ ] T013 [P] Add todo_ownership_guardrail (output) to backend/app/agents/guardrails.py
- [ ] T014 Create backend/app/agents/tools.py module with function tool decorators imported
- [ ] T015 Create backend/app/agents/agents.py for agent definitions (empty structure)
- [ ] T016 Create backend/app/agents/runner.py with basic agent execution wrapper
- [ ] T017 Create backend/app/api/v1/chat.py with FastAPI router stub
- [ ] T018 [P] Create frontend/components/chat/ directory for chat UI components
- [ ] T019 [P] Create frontend/lib/validations/chat.schema.ts with Zod schemas for chat messages
- [ ] T020 [P] Create frontend/hooks/useChat.ts hook structure (empty implementation)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Todo Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create todos through natural conversation on /dashboard

**Independent Test**: Log in, navigate to /dashboard, send "Add a task to test the chatbot", verify todo appears in user's list

### Implementation for User Story 1

#### Backend: TodoManagerAgent with Create Tool

- [ ] T021 [P] [US1] Define CreateTodoInput Pydantic model in backend/app/agents/models.py
- [ ] T022 [P] [US1] Define CreateTodoOutput Pydantic model in backend/app/agents/models.py
- [ ] T023 [US1] Implement create_todo function tool in backend/app/agents/tools.py using @function_tool decorator
- [ ] T024 [US1] Implement get_todos function tool in backend/app/agents/tools.py (needed for verification)
- [ ] T025 [US1] Define TodoManagerAgent in backend/app/agents/agents.py with create_todo and get_todos tools
- [ ] T026 [US1] Add TodoManagerAgent instructions for parsing natural language todo creation commands
- [ ] T027 [US1] Attach guardrails (user_authorization, input_sanitization, rate_limit) to TodoManagerAgent
- [ ] T028 [US1] Implement agent runner function in backend/app/agents/runner.py with session management
- [ ] T029 [US1] Add exception handling (InputGuardrailTripwireTriggered, ModelBehaviorError) to runner

#### Backend: Chat API Endpoints

- [ ] T030 [US1] Implement POST /api/v1/chat/message endpoint in backend/app/api/v1/chat.py
- [ ] T031 [US1] Extract user_id from authentication middleware in chat endpoint
- [ ] T032 [US1] Create or retrieve session in chat endpoint using sessions.py functions
- [ ] T033 [US1] Pass user_id context to Runner.run() in chat endpoint
- [ ] T034 [US1] Return ChatResponse with message, action_performed, todos_affected fields
- [ ] T035 [US1] Add error handling for guardrail triggers (401, 403, 429 errors)
- [ ] T036 [US1] Register chat router in backend/app/main.py

#### Frontend: Chat UI Components

- [ ] T037 [P] [US1] Create ChatMessage.tsx Server Component in frontend/components/chat/
- [ ] T038 [P] [US1] Create ChatInput.tsx Client Component with form validation in frontend/components/chat/
- [ ] T039 [P] [US1] Create AgentStatus.tsx loading indicator component in frontend/components/chat/
- [ ] T040 [US1] Create MessageList.tsx scrollable container in frontend/components/chat/
- [ ] T041 [US1] Create ChatWindow.tsx Client Component orchestrating all chat UI in frontend/components/chat/
- [ ] T042 [US1] Style chat components with TailwindCSS (message bubbles, input, loading states)

#### Frontend: Chat State Management

- [ ] T043 [US1] Implement useChat hook with messages state in frontend/hooks/useChat.ts
- [ ] T044 [US1] Add sendMessage function to useChat hook calling POST /api/v1/chat/message
- [ ] T045 [US1] Add isLoading state management to useChat hook
- [ ] T046 [US1] Add error handling to useChat hook (network errors, auth errors, rate limits)
- [ ] T047 [US1] Update frontend/lib/api-client.ts with chat API methods
- [ ] T048 [US1] Add ChatMessage type to frontend/lib/types.ts

#### Frontend: Dashboard Integration

- [ ] T049 [US1] Update frontend/app/dashboard/page.tsx to import ChatWindow component
- [ ] T050 [US1] Add ChatWindow to dashboard page layout (authenticated users only)
- [ ] T051 [US1] Verify authentication check prevents unauthenticated access to chat UI

**Checkpoint**: At this point, users can create todos via natural language chat on /dashboard

---

## Phase 4: User Story 2 - Todo Management via Chat (Priority: P2)

**Goal**: Enable users to update, complete, and delete todos through conversation

**Independent Test**: Create a todo, then send "Mark the test task as complete", "Update task X to be due tomorrow", "Delete task Y" and verify changes

### Implementation for User Story 2

#### Backend: Additional CRUD Tools

- [ ] T052 [P] [US2] Define UpdateTodoInput Pydantic model in backend/app/agents/models.py
- [ ] T053 [P] [US2] Define UpdateTodoOutput Pydantic model in backend/app/agents/models.py
- [ ] T054 [P] [US2] Define DeleteTodoInput and DeleteTodoOutput models in backend/app/agents/models.py
- [ ] T055 [P] [US2] Implement update_todo function tool in backend/app/agents/tools.py
- [ ] T056 [P] [US2] Implement delete_todo function tool in backend/app/agents/tools.py
- [ ] T057 [P] [US2] Implement search_todos function tool in backend/app/agents/tools.py
- [ ] T058 [US2] Add update_todo, delete_todo, search_todos to TodoManagerAgent tools list
- [ ] T059 [US2] Update TodoManagerAgent instructions to handle update, delete, and status change commands
- [ ] T060 [US2] Add ownership verification in delete_todo tool (check user_id before deletion)
- [ ] T061 [US2] Add confirmation prompt logic for delete operations in agent instructions

#### Frontend: Enhanced Chat Interactions

- [ ] T062 [US2] Update ChatMessage component to display action_performed indicators (update, delete icons)
- [ ] T063 [US2] Add todos_affected display to show which todos were modified in ChatMessage
- [ ] T064 [US2] Update useChat hook to handle follow-up messages (session_id persistence)
- [ ] T065 [US2] Add clarification prompt handling in ChatWindow (display agent questions)

**Checkpoint**: At this point, users can create, read, update, and delete todos via chat

---

## Phase 5: User Story 3 - Conversational Todo Queries (Priority: P3)

**Goal**: Enable users to query their todos using natural language ("What's due today?", "Show overdue tasks")

**Independent Test**: Create todos with different due dates, ask "What's due tomorrow?", "Show completed tasks", verify correct filtered results

### Implementation for User Story 3

#### Backend: AnalyticsAgent with Query Tools

- [ ] T066 [P] [US3] Define FilterByDateInput and FilterByDateOutput models in backend/app/agents/models.py
- [ ] T067 [P] [US3] Define FilterByStatusInput and FilterByStatusOutput models in backend/app/agents/models.py
- [ ] T068 [P] [US3] Define TodoStatsOutput model in backend/app/agents/models.py
- [ ] T069 [P] [US3] Implement filter_todos_by_date function tool in backend/app/agents/tools.py
- [ ] T070 [P] [US3] Implement filter_todos_by_status function tool in backend/app/agents/tools.py
- [ ] T071 [P] [US3] Implement get_todo_statistics function tool in backend/app/agents/tools.py
- [ ] T072 [US3] Define AnalyticsAgent in backend/app/agents/agents.py with analytics tools
- [ ] T073 [US3] Add AnalyticsAgent instructions for query interpretation and filtering
- [ ] T074 [US3] Attach guardrails (user_authorization, todo_ownership) to AnalyticsAgent

#### Backend: Agent Handoffs

- [ ] T075 [US3] Add handoff(AnalyticsAgent) to TodoManagerAgent handoffs list
- [ ] T076 [US3] Update TodoManagerAgent instructions with triage policy (when to handoff to Analytics)
- [ ] T077 [US3] Update runner.py to support agent handoffs (if not already handled by SDK)
- [ ] T078 [US3] Add handoff event logging in runner.py for observability

#### Frontend: Query Results Display

- [ ] T079 [US3] Update ChatMessage component to render todo lists (from analytics queries)
- [ ] T080 [US3] Add todo count badges to ChatMessage for statistics display
- [ ] T081 [US3] Style filtered todo lists with TailwindCSS (overdue in red, completed in green)

**Checkpoint**: All three user stories are now independently functional - full chatbot capabilities complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Observability & Monitoring

- [ ] T082 [P] Add set_tracing_export_api_key() to backend/app/agents/config.py for OpenAI tracing
- [ ] T083 [P] Implement structured JSON logging in backend/app/agents/runner.py (user_id, session_id, agent_name, tool_name fields)
- [ ] T084 [P] Add Prometheus metrics in backend/app/api/v1/chat.py (chat_requests_total, chat_response_duration_seconds counters)
- [ ] T085 [P] Add correlation IDs (session_id) to all log messages

### Error Handling & Edge Cases

- [ ] T086 [P] Add MaxTurnsExceeded exception handling to runner with user-friendly message
- [ ] T087 [P] Add OutputGuardrailTripwireTriggered handling with security logging
- [ ] T088 [P] Handle ambiguous commands in TodoManagerAgent (ask clarifying questions)
- [ ] T089 Add retry logic for transient tool failures (network errors, timeouts)

### Frontend Polish

- [ ] T090 [P] Add responsive design verification for chat UI (mobile 320px+, desktop 1024px+)
- [ ] T091 [P] Add empty state message to ChatWindow ("Start a conversation to manage your todos")
- [ ] T092 [P] Add rate limit error display in useChat hook (429 → "Too many requests, please wait")
- [ ] T093 [P] Add session timeout handling in useChat (auto-reset after 24 hours)
- [ ] T094 Add shadcn/ui Button, Card, Input components to chat UI if not already using

### Documentation & Deployment

- [ ] T095 [P] Create backend smoke test script at backend/scripts/smoke_test.py per agent-architecture-plan.md
- [ ] T096 [P] Add agent setup instructions to backend/README.md (OPENAI_API_KEY, .agent-sessions/ setup)
- [ ] T097 [P] Document chat API endpoints in backend API documentation (OpenAPI schema)
- [ ] T098 Update frontend/README.md with chat feature usage instructions

### Security Hardening

- [ ] T099 Verify todo_ownership_guardrail prevents cross-user access in all analytics tools
- [ ] T100 Add input length validation (2000 char limit) to chat endpoint before agent processing
- [ ] T101 Verify rate limiting works across multiple sessions (test 31 requests in 1 minute)
- [ ] T102 Add security audit logging for guardrail trigger events

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - **US1 (P1)** can start after Phase 2 - No dependencies on other stories
  - **US2 (P2)** can start after Phase 2 - Extends US1 but independently testable
  - **US3 (P3)** can start after Phase 2 - Uses US1/US2 tools but independently testable
- **Polish (Phase 6)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1) - Todo Creation**: Can start after Foundational (Phase 2) - INDEPENDENT
- **User Story 2 (P2) - Todo Management**: Can start after Foundational (Phase 2) - INDEPENDENT (adds more tools to same agent)
- **User Story 3 (P3) - Conversational Queries**: Can start after Foundational (Phase 2) - INDEPENDENT (new agent with handoffs)

### Within Each User Story

User Story 1:
- T021-T022 (models) before T023-T024 (tools)
- T023-T024 (tools) before T025 (agent definition)
- T025 (agent) before T028 (runner)
- T028 (runner) before T030 (API endpoint)
- T037-T039 (components) can be parallel
- T037-T041 (UI) before T043 (hook)
- T043 (hook) before T049 (dashboard integration)

User Story 2:
- T052-T054 (models) before T055-T057 (tools)
- T055-T057 (tools) before T058 (agent update)
- T058 (agent) before T059 (instructions)
- T062-T063 (UI updates) can be parallel

User Story 3:
- T066-T068 (models) before T069-T071 (tools)
- T069-T071 (tools) before T072 (agent definition)
- T072 (Analytics agent) before T075 (handoff setup)
- T075-T076 (handoffs) before T077 (runner update)
- T079-T081 (UI updates) can be parallel

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- T002, T003, T004, T005 can all run in parallel

**Foundational Phase (Phase 2)**:
- T007, T008, T009 can run in parallel
- T010, T011, T012, T013 can run in parallel (all guardrails)
- T018, T019, T020 can run in parallel (all frontend foundation)

**User Story 1**:
- T021, T022 can run in parallel (models)
- T037, T038, T039 can run in parallel (UI components)

**User Story 2**:
- T052, T053, T054 can run in parallel (models)
- T055, T056, T057 can run in parallel (tools)

**User Story 3**:
- T066, T067, T068 can run in parallel (models)
- T069, T070, T071 can run in parallel (tools)
- T079, T080, T081 can run in parallel (UI updates)

**Polish Phase (Phase 6)**:
- T082, T083, T084, T085 can run in parallel (observability)
- T086, T087, T088, T089 can run in parallel (error handling)
- T090, T091, T092, T093, T094 can run in parallel (frontend polish)
- T095, T096, T097, T098 can run in parallel (documentation)

---

## Parallel Example: User Story 1

```bash
# After Foundational phase completes, these can run in parallel:

# Terminal 1: Backend models and tools
task T021  # CreateTodoInput model
task T022  # CreateTodoOutput model (parallel with T021)
task T023  # create_todo tool (after T021, T022)
task T024  # get_todos tool (parallel with T023)

# Terminal 2: Backend agent and API
task T025  # TodoManagerAgent definition (after T023, T024)
task T026  # Agent instructions (parallel with T025)
task T027  # Attach guardrails (after T025)
task T028  # Agent runner (after T027)
task T030  # Chat endpoint (after T028)

# Terminal 3: Frontend components (can start immediately after Phase 2)
task T037  # ChatMessage component
task T038  # ChatInput component (parallel with T037)
task T039  # AgentStatus component (parallel with T037, T038)
task T040  # MessageList component (after T037)
task T041  # ChatWindow component (after T037-T040)

# Terminal 4: Frontend state management
task T043  # useChat hook (after T041)
task T044  # sendMessage function (parallel with T043)
task T045  # isLoading state (parallel with T043, T044)
```

**Parallel Execution Strategy**: With 4 developers, User Story 1 can be completed with minimal blocking. Models → Tools → Agent → API is the critical path, while UI can proceed independently.

---

## Implementation Strategy

### MVP Scope (Recommended First Iteration)

**Phase 1 + Phase 2 + Phase 3 (User Story 1 only)**

This delivers the core value: Users can create todos via natural language chat on /dashboard.

**Estimated Tasks**: T001-T051 (51 tasks)

**Why this is MVP**:
- Demonstrates agent functionality (natural language processing, tool execution)
- Delivers immediate user value (faster todo creation vs forms)
- Tests all infrastructure (agents, tools, guardrails, sessions, API, UI)
- Independently testable and deployable

### Incremental Delivery

**Iteration 2**: Add Phase 4 (User Story 2) - CRUD operations
- **Tasks**: T052-T065 (14 tasks)
- **Value**: Complete todo management without leaving chat interface

**Iteration 3**: Add Phase 5 (User Story 3) - Analytics queries
- **Tasks**: T066-T081 (16 tasks)
- **Value**: Powerful query interface ("What's overdue?", "Show today's tasks")

**Iteration 4**: Add Phase 6 (Polish)
- **Tasks**: T082-T102 (21 tasks)
- **Value**: Production-ready observability, security, documentation

### Validation Checkpoints

After each phase:
1. Run smoke test (if available)
2. Verify independent test criteria for each user story
3. Check authentication/authorization works
4. Verify guardrails prevent unauthorized access
5. Measure response time (<3s for 95% of requests)

---

## Task Summary

**Total Tasks**: 102

**Breakdown by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 15 tasks
- Phase 3 (US1 - Todo Creation): 31 tasks
- Phase 4 (US2 - Todo Management): 14 tasks
- Phase 5 (US3 - Queries): 16 tasks
- Phase 6 (Polish): 21 tasks

**Breakdown by User Story**:
- US1 (Natural Language Todo Creation): 31 tasks
- US2 (Todo Management via Chat): 14 tasks
- US3 (Conversational Todo Queries): 16 tasks
- Infrastructure (Setup + Foundational): 20 tasks
- Polish & Cross-cutting: 21 tasks

**Parallel Opportunities**: 47 tasks marked with [P] can run in parallel within their phase

**MVP Scope**: 51 tasks (Phase 1 + Phase 2 + Phase 3)

**Critical Path**: Setup → Foundational → US1 Models → US1 Tools → US1 Agent → US1 API → US1 UI Integration

---

## Next Steps

1. **Start with Phase 1 (Setup)**: Install dependencies and configure environment
2. **Complete Phase 2 (Foundational)**: Build agent infrastructure (guardrails, sessions, base structure)
3. **Implement User Story 1 (MVP)**: Deliver natural language todo creation
4. **Validate MVP**: Test independently per acceptance criteria
5. **Iterate**: Add US2, US3, and Polish based on priority and feedback

**Ready to begin implementation!** 🚀
