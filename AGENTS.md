# AGENT.md: Todo Web App AI Agent

## Agent Mission
You are an expert AI assistant **Todo Web App Agent** - Your task is to generate the code while abiding yourself to the rules. You ensure 100% compliance with the v1.0.0 Constitution while accelerating development through:

- **Code generation** aligned with all 10 Core Principles
- **Architecture audits** catching violations before PRs
- **Spec generation** using `.specify/templates/` standards
- **Optimization suggestions** within performance constraints
- **Dependency justification** per Principle VIII

---

## Architecture Overview: Better Auth + FastAPI Hybrid

This is a full-stack Todo Web App with authentication handled by Better Auth (Next.js) and business logic by FastAPI:

```
┌─────────────────────────────────────────────────┐
│              Next.js Frontend                   │
│         (Better Auth + UI Components)           │
└─────────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌────────────────┐      ┌────────────────┐
│  Better Auth   │      │   FastAPI      │
│  - Users table │      │  - Todos table │
│  - Sessions    │◄─────┤  - Validates   │
│  - JWT + Cookie│      │    JWT token   │
└────────────────┘      └────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
              ┌──────────────┐
              │ PostgreSQL   │
              │ (Neon)       │
              └──────────────┘
```

**Division of Responsibilities:**
- **Better Auth**: User registration, login, JWT generation, session management
- **FastAPI**: JWT validation, todo CRUD operations
- **Frontend**: Bridges Better Auth and FastAPI, handles UI
- **Shared**: PostgreSQL database, JWT secret key

---

## Constitutional Alignment Matrix

| Principle | Enforcement Strategy | Key Artifacts |
|-----------|---------------------|---------------|
| **I. Component-First** | Single-responsibility React Server Components | `TodoItem.tsx`, `TodoList.tsx` |
| **II. Type Safety** | TS + Pydantic + SQLModel | Full type chains, no `any` |
| **III. Server-Client** | Server Components 80%+ | `'use server'` directives |
| **IV. Predictable Flow** | Props-down, hooks-up | Custom hooks + Zod schemas |
| **V. Styling System** | Tailwind + shadcn/ui | `cn()` utility classes |
| **VI. API-First** | FastAPI + Pydantic | FastAPI routers + Pydantic |
| **VII. Performance** | SSR/SSG/streaming | Next.js app router patterns |
| **VIII. Tooling** | Justified only | SWR + rationale |
| **IX. Data Modeling** | SQLModel + Neon | Alembic migrations |
| **X. Error Handling** | Typed HTTP responses | Custom error boundaries |

---

## Technology Stack

### Frontend
```
├── Next.js 16.1.1 (App Router)
├── React 19.2.3
├── TypeScript 5.x
├── TailwindCSS 4.x (PostCSS)
├── shadcn/ui (primitives only)
├── Better Auth 1.4.10 (authentication)
├── SWR 2.3.8 (data fetching)
├── Zod 4.3.4 + React Hook Form 7.69.0
├── jose 5.9.0 (JWT for FastAPI bridge)
├── Zustand 5.0.9 (client state)
└── Sonner 2.0.7 (toasts)
```

### Backend
```
├── FastAPI 0.128+
├── Pydantic v2 + pydantic-settings 2.12.0
├── SQLModel 0.0.31
├── asyncpg 0.31.0 (async PostgreSQL)
├── python-jose 3.5.0 (JWT validation)
├── Alembic 1.17.2 (migrations)
└── UV (Python 3.13 package mgmt)
```

### Database
```
└── Neon PostgreSQL (serverless, connection pooling)
```

---

## Project Structure

### Root Directory
```
Phase3/
├── frontend/           # Next.js 16 application
├── backend/            # FastAPI application
├── .specify/           # SpecKit Plus templates & scripts
├── specs/              # Feature specifications
├── history/            # PHRs and ADRs
├── AGENTS.md           # This file (Agent mission & rules)
├── CLAUDE.md           # Claude Code development rules
└── README.md           # Project overview
```

### Frontend Structure (`frontend/`)
```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout (Server Component)
│   ├── page.tsx                 # Landing page (Server Component)
│   ├── globals.css              # Tailwind base styles
│   ├── loading.tsx              # Global loading
│   ├── not-found.tsx            # 404 page
│   ├── (auth)/                  # Auth route group
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── dashboard/               # Protected dashboard routes
│   │   ├── layout.tsx           # Dashboard layout with sidebar
│   │   ├── page.tsx             # Dashboard home (stats)
│   │   └── todos/
│   │       ├── page.tsx         # Todo list
│   │       └── [id]/
│   │           ├── page.tsx     # Todo detail
│   │           └── not-found.tsx
│   └── api/auth/[...better-auth]/route.ts  # Better Auth API handler
│
├── actions/                      # Server Actions
│   ├── auth.actions.ts          # getSession, requireAuth
│   └── todo.actions.ts          # createTodo, toggleTodo, deleteTodo
│
├── components/
│   ├── auth/                    # Auth components
│   │   ├── AuthCard.tsx
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── dashboard/               # Dashboard components
│   │   ├── AppSidebar.tsx       # Main sidebar (shadcn)
│   │   └── UserProfile.tsx      # User profile in sidebar
│   ├── landing/                 # Landing page components
│   │   ├── CTASection.tsx
│   │   ├── FeatureCard.tsx
│   │   ├── FeaturesGrid.tsx
│   │   └── Hero.tsx
│   ├── shared/                  # Shared components
│   │   ├── ErrorBoundary.tsx
│   │   ├── Footer.tsx
│   │   └── Header.tsx
│   ├── todos/                   # Todo components
│   │   ├── TodoDetail.tsx
│   │   ├── TodoItem.tsx
│   │   └── TodoList.tsx
│   └── ui/                      # shadcn/ui primitives
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── checkbox.tsx
│       ├── dropdown-menu.tsx
│       ├── form.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── navigation-menu.tsx
│       ├── separator.tsx
│       ├── sheet.tsx
│       ├── sidebar.tsx
│       ├── skeleton.tsx
│       └── tooltip.tsx
│
├── hooks/                        # Custom React hooks
│   ├── use-mobile.ts            # Mobile detection (sidebar)
│   ├── use-stats.ts             # SWR hook for todo stats
│   └── use-todos.ts             # SWR hook for todos
│
├── lib/                          # Utilities & core logic
│   ├── api-client.ts            # FastAPI client (apiRequest, api.get/post/patch/delete)
│   ├── auth.ts                  # Better Auth server config (pg driver)
│   ├── auth-client.ts           # Better Auth client (signIn, signUp, signOut, useSession)
│   ├── backend-jwt.ts           # JWT issuer for FastAPI (issueBackendJwt)
│   ├── constants.ts             # Theme constants
│   ├── db.ts                    # Postgres pool (pg)
│   ├── types.ts                 # Shared TypeScript types
│   ├── utils.ts                 # cn() utility
│   └── validations/             # Zod schemas
│       ├── auth.schema.ts       # loginSchema, registerSchema
│       └── todo.schema.ts       # todoSchema, createTodoSchema
│
├── middleware.ts                 # Route protection
├── next.config.ts
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

### Backend Structure (`backend/`)
```
backend/
├── app/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, exception handlers
│   ├── config.py                # Pydantic settings (DB, JWT config)
│   │
│   ├── models/                  # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py              # Better Auth's users table (READ-ONLY)
│   │   └── todo.py              # Todos table (owned by FastAPI)
│   │
│   ├── schemas/                 # Pydantic schemas (API contracts)
│   │   ├── __init__.py
│   │   ├── todo.py              # TodoCreate, TodoUpdate, TodoResponse, TodoStats
│   │   └── common.py            # ErrorResponse, PaginationParams
│   │
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   ├── deps.py              # get_current_user, get_session dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # Main v1 router
│   │       ├── todos.py         # Todo CRUD endpoints
│   │       ├── stats.py         # Todo statistics endpoint
│   │       └── auth.py          # /auth/me endpoint
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   └── todo_service.py      # Todo CRUD operations
│   │
│   ├── db/                      # Database layer
│   │   ├── __init__.py
│   │   └── session.py           # Async DB session factory (Neon)
│   │
│   └── core/                    # Core utilities
│       ├── __init__.py
│       ├── security.py          # JWT validation (verify_token)
│       └── exceptions.py        # Custom exceptions + handlers
│
├── .python-version               # Python 3.13
├── pyproject.toml                # UV dependencies
├── uv.lock                       # UV lock file
├── .env                          # Environment variables (gitignored)
└── CLAUDE.md                     # Backend development rules
```

---

## Authentication Flow

### 1. Better Auth (Frontend)

**Server Config** (`lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth"
import { Pool } from "pg"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
  database: pool,
  emailAndPassword: { enabled: true },
  plugins: [jwt()],
})
```

**Client** (`lib/auth-client.ts`):
```typescript
import { createAuthClient } from "better-auth/react"
export const { signIn, signUp, signOut, useSession } = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL,
})
```

### 2. JWT Bridge for FastAPI

**Issue JWT** (`lib/backend-jwt.ts`):
```typescript
import { SignJWT } from "jose"

export async function issueBackendJwt(userId: string): Promise<string> {
  const secret = new TextEncoder().encode(process.env.BETTER_AUTH_SECRET)
  return await new SignJWT({})
    .setSubject(userId)
    .setIssuedAt()
    .setExpirationTime("1h")
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .sign(secret)
}
```

### 3. FastAPI JWT Validation

**Dependency** (`app/api/deps.py`):
```python
async def get_current_user(
    payload: Annotated[dict, Depends(verify_token)],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    # 1. verify_token decodes JWT using shared SECRET_KEY
    # 2. Extract user_id from payload["sub"]
    # 3. Query Better Auth's users table
    # 4. Return User object or raise 401
```

### 4. Route Protection

**Middleware** (`middleware.ts`):
```typescript
export function middleware(request: NextRequest) {
  const sessionCookie = getSessionCookie(request)

  // Redirect authenticated users from login/register
  if (sessionCookie && ['/login', '/register'].includes(pathname)) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // Protect dashboard routes
  if (!sessionCookie && pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}
```

---

## API Endpoints

### Backend (FastAPI)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (no auth) |
| `/api/v1/auth/me` | GET | Get current user profile |
| `/api/v1/todos` | GET | List user's todos |
| `/api/v1/todos` | POST | Create todo (201) |
| `/api/v1/todos/{id}` | PATCH | Update todo |
| `/api/v1/todos/{id}` | DELETE | Delete todo (204) |
| `/api/v1/users/me/todos/stats` | GET | Get todo statistics |

### Database Models

**User** (Better Auth - READ-ONLY):
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # String UUID from Better Auth
    email: str
    name: Optional[str]
    email_verified: bool
    created_at: datetime
    updated_at: datetime
```

**Todo** (FastAPI-owned):
```python
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str
    description: Optional[str]
    completed: bool = Field(default=False)  # Maps to is_completed column
    priority: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    user_id: str = Field(foreign_key="user.id")
    created_at: datetime
    updated_at: datetime
```

---

## Type Definitions

### Frontend Types (`lib/types.ts`)
```typescript
export interface User {
  id: string
  email: string
  name?: string
  image?: string
}

export interface Todo {
  id: number
  title: string
  description?: string
  completed: boolean
  priority: "LOW" | "MEDIUM" | "HIGH"
  user_id: string
  created_at: string
  updated_at: string
}

export interface ApiError {
  detail: string
  status_code?: number
}
```

---

## Styling System

### Theme Colors
- `primary`: #f4252f (red)
- `obsidian`: #050505 (background)
- `charcoal`: #121212 (cards)
- `border-subtle`: #2a2a2a
- `border-sharp`: #444444

### shadcn/ui Components
All primitives in `components/ui/`. Use `cn()` utility for class merging:
```typescript
import { cn } from "@/lib/utils"
<Button className={cn("custom-class", condition && "conditional-class")} />
```

---

## File Naming Conventions

### Frontend Files
- **Components**: `PascalCase.tsx` (e.g., `TodoList.tsx`)
- **Utilities**: `kebab-case.ts` (e.g., `api-client.ts`)
- **Hooks**: `use-*.ts` or `use*.ts` (e.g., `use-todos.ts`)
- **Actions**: `*.actions.ts` (e.g., `todo.actions.ts`)
- **Schemas**: `*.schema.ts` (e.g., `todo.schema.ts`)

### Backend Files
- **Modules**: `snake_case.py` (e.g., `todo_service.py`)
- **Models**: `snake_case.py` in `models/`
- **Schemas**: `snake_case.py` in `schemas/`

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `frontend/lib/auth.ts` | Better Auth server config (uses `pg` directly) |
| `frontend/lib/auth-client.ts` | Better Auth client exports |
| `frontend/lib/backend-jwt.ts` | JWT issuer for FastAPI communication |
| `frontend/lib/api-client.ts` | FastAPI HTTP client |
| `frontend/lib/types.ts` | Shared TypeScript interfaces |
| `frontend/actions/auth.actions.ts` | Server actions for auth |
| `frontend/actions/todo.actions.ts` | Server actions for todo CRUD |
| `frontend/middleware.ts` | Route protection |
| `frontend/app/dashboard/layout.tsx` | Dashboard layout with AppSidebar |
| `backend/app/api/deps.py` | get_current_user, get_session dependencies |
| `backend/app/core/security.py` | JWT validation (verify_token) |
| `backend/app/services/todo_service.py` | Todo CRUD operations |

---

## Environment Variables

### Frontend (.env)
```bash
# Better Auth
BETTER_AUTH_SECRET="your-secret-key"
BETTER_AUTH_URL="http://localhost:3000"
NEXT_PUBLIC_AUTH_URL="http://localhost:3000"

# Database (Neon PostgreSQL)
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"

# FastAPI Backend
NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
```

### Backend (.env)
```bash
# Database (Neon PostgreSQL)
DATABASE_URL="postgresql+asyncpg://user:pass@host/db"

# JWT (MUST match Better Auth)
JWT_SECRET_KEY="your-secret-key"
JWT_ALGORITHM="HS256"

# API
API_V1_PREFIX="/api/v1"
CORS_ORIGINS="http://localhost:3000"

# Server
HOST="0.0.0.0"
PORT=8000
ENVIRONMENT="development"
```

---

## Security Rules

### Critical Rules
- **NEVER** generate JWT tokens in backend (Better Auth does this)
- **NEVER** create users in backend (Better Auth does this)
- **ALWAYS** validate JWT on every FastAPI request
- **ALWAYS** filter by user_id for authorization
- JWT secret **MUST** match Better Auth's secret
- Never expose `BETTER_AUTH_SECRET` to client

### User ID Type
- User ID is **string** (Better Auth generates UUIDs)
- Not `int` - this is critical for type safety

---

## Red Lines (Constitution Breaches)

```
❌ Custom CSS (Principle V) - Use Tailwind only
❌ 'any' types (Principle II) - Full type coverage required
❌ Client Components first (Principle III) - Server Components 80%+
❌ Unvalidated inputs (Principles II, VI) - Use Zod/Pydantic
❌ External libs without justification (VIII)
❌ Silent error handling (Principle X) - Always surface errors
❌ JWT generation in FastAPI - Better Auth only
❌ User creation in FastAPI - Better Auth only
```

---

## Development Commands

### Frontend
```bash
npm install          # Install dependencies
npm run dev          # Development server (localhost:3000)
npm run build        # Production build
npm start            # Start production server
```

### Backend
```bash
uv sync              # Install dependencies
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
curl http://localhost:8000/health  # Health check
```

---

## Success Metrics
- **0 constitution violations** per PR
- **80%+ Server Components**
- **100% type coverage**
- **< 100ms API response** (P95)
- **CI passes first time** 95%+

---

**Version**: 2.0.0 | **Updated**: 2026-01-21 | **Architecture**: Better Auth + FastAPI Hybrid
