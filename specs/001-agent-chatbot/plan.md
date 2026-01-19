# Implementation Plan: AI Agent Chatbot for Todo Management

**Branch**: `001-agent-chatbot` | **Date**: 2026-01-15 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-agent-chatbot/spec.md`

## Summary

This feature adds an AI-powered chatbot to the Todo Web App that enables natural language todo management. The chatbot is accessible only on the `/dashboard` route for authenticated users and uses the OpenAI Agents SDK (Python) to interpret natural language commands and execute CRUD operations on todos. The system consists of specialized agents (Todo Manager, Analytics Agent) that use function tools to interact with existing backend APIs. The architecture emphasizes security (user-scoped operations only), performance (async operations, streaming responses), and maintainability (typed interfaces, guardrails, structured outputs).

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: `openai-agents`, FastAPI 0.115+, Pydantic v2, SQLModel, Neon PostgreSQL
- Frontend: Next.js 16.1.1, React 19.2.3, TailwindCSS 4.x
**Storage**: Neon PostgreSQL (existing) + SQLite sessions for agent conversation context
**Testing**: pytest (backend), Vitest/Jest (frontend)
**Target Platform**: FastAPI service (backend), Next.js web app (frontend)
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- Agent response time: <3s for 95% of requests
- Natural language command accuracy: 90%+
- API throughput: existing constraints (inherit from todo CRUD APIs)
**Constraints**:
- Auth-only access (no unauthenticated chatbot use)
- User-scoped operations (agent cannot access other users' todos)
- Stateless frontend sessions (context resets on page refresh initially)
- No persistent chat history across sessions (v1 limitation)
**Scale/Scope**:
- Support for 2 specialized agents
- 8 function tools (CRUD operations, queries, filters)
- ~500-1000 lines of agent orchestration code
- Frontend: 5-8 React components for chat UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### ✅ Passes

1. **Component-First Design (I)**: Chat UI will be composed of small, isolated React components (ChatMessage, ChatInput, ChatWindow, AgentStatus)
2. **Type Safety by Default (II)**: All agent tools use Pydantic models; frontend uses TypeScript with explicit types; Zod schemas for message validation
3. **Server-Client Clarity (III)**: Chat message display uses Server Components where possible; only input and real-time updates require Client Components
4. **Predictable Data Flow (IV)**: Agent tools have explicit input/output schemas; chat state flows top-down through props/hooks
5. **Styling as a System (V)**: TailwindCSS for all chat UI styling; shadcn/ui primitives for input, message bubbles, loading states
6. **API-First Design (VI)**: Agent tools call existing validated FastAPI endpoints; tool schemas match API contracts
7. **Performance-Aware Rendering (VII)**: Streaming agent responses; async tool execution; Server Components for static chat elements
8. **Tooling by Necessity (VIII)**: OpenAI Agents SDK justified (core requirement); SQLite sessions (SDK recommendation); no unnecessary dependencies
9. **Explicit Data Modeling (IX)**: Chat sessions modeled with SQLite; agent tool calls reference existing Todo SQLModel entities
10. **Deterministic Error Handling (X)**: Guardrails trigger on invalid operations; typed exceptions mapped to user-friendly messages

### ⚠️ Requires Justification

- **New dependency**: openai-agents package - JUSTIFIED by feature requirement (spec explicitly requires OpenAI Agents SDK)
- **SQLite for sessions**: Adds new storage mechanism - JUSTIFIED by SDK recommendation for conversation context management

## Project Structure

### Documentation (this feature)

```
specs/001-agent-chatbot/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```
backend/
├── app/
│   ├── agents/                    # NEW
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── models.py
│   │   ├── tools.py
│   │   ├── guardrails.py
│   │   ├── agents.py
│   │   ├── runner.py
│   │   └── sessions.py
│   ├── api/v1/
│   │   └── chat.py               # NEW
│   ├── services/
│   │   └── todo_service.py       # EXISTING
│   └── tests/
│       └── test_agents/          # NEW
│           ├── test_tools.py
│           ├── test_guardrails.py
│           └── test_agents.py
├── .agent-sessions/               # NEW (gitignored)
└── pyproject.toml                 # UPDATE

frontend/
├── app/dashboard/
│       └── page.tsx              # UPDATE
├── components/chat/              # NEW
│   ├── ChatWindow.tsx
│   ├── ChatMessage.tsx
│   ├── ChatInput.tsx
│   ├── AgentStatus.tsx
│   └── MessageList.tsx
├── lib/
│   ├── api-client.ts             # UPDATE
│   ├── types.ts                  # UPDATE
│   └── validations/
│       └── chat.schema.ts        # NEW
└── hooks/
    └── useChat.ts                # NEW
```

**Structure Decision**: Web application structure selected. Backend adds /agents module and /api/v1/chat endpoints. Frontend adds /components/chat for UI. Follows existing conventions.

## Complexity Tracking

No violations requiring justification beyond the two noted above (both justified by feature requirements).


---

# Production-Grade Multi-Agent System Design

See [agent-architecture-plan.md](./agent-architecture-plan.md) for the complete production-grade multi-agent architecture including:

1. **Scope & Assumptions** - What's in/out of scope, key assumptions
2. **Agent Inventory** - TodoManagerAgent, AnalyticsAgent with routing/handoffs
3. **Tools (8 function tools)** - Complete schemas and implementations for all CRUD and analytics operations
4. **Context Strategy** - SQLite session management, user context handling
5. **Guardrails** - Input (auth, sanitization, rate limit) and output (ownership) guardrails with tripwire handling
6. **Structured Outputs** - Pydantic models ensuring reliable JSON responses
7. **MCP Integration** - Deferred to future phase per user request
8. **Observability** - Tracing, logging, metrics (Prometheus)
9. **Failure Handling** - Exception handling, retries, max turns, fallbacks
10. **Test Plan** - Unit tests, integration tests, smoke test
11. **Deployment Checklist** - Step-by-step deployment guide
12. **Acceptance Criteria** - Measurable success criteria for backend, frontend, security, performance

---

# Phase 0: Research (Next Steps)

The `/sp.plan` command will now generate `research.md` to resolve any remaining NEEDS CLARIFICATION items and document best practices for:

- **Agent architecture patterns**: Best practices for multi-agent systems with handoffs
- **Session management**: SQLite vs Redis vs in-memory, cleanup strategies
- **Guardrail strategies**: When to use input vs output guardrails, performance impact
- **Natural language date parsing**: Libraries and techniques for parsing "tomorrow", "next Friday", etc.
- **Streaming responses**: SSE vs WebSocket tradeoffs for real-time agent updates
- **Error recovery**: Handling API failures, model timeouts, guardrail triggers gracefully

This research will inform the Phase 1 design artifacts.

---

# Phase 1: Design & Contracts (After Phase 0)

Will generate:

1. **data-model.md**: Detailed schemas for agents, sessions, tool I/O, chat messages
2. **contracts/**: OpenAPI/JSON schemas for all tools and API endpoints
3. **quickstart.md**: Developer setup guide for running agents locally

---

# Phase 2: Tasks (After Phase 1)

Run `/sp.tasks` to generate detailed implementation tasks with test cases based on this plan.

---

**Plan Status**: ✅ Complete (awaiting Phase 0 research execution)
**Plan Date**: 2026-01-15
**Approved By**: Pending user review

