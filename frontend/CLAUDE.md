# Frontend Development Rules

## Architecture Overview: Next.js + Better Auth + FastAPI

**This frontend works in conjunction with Better Auth (authentication) and FastAPI (business logic):**

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
- **Better Auth**: User registration, login, session management, JWT generation
- **FastAPI**: JWT validation, todo CRUD operations
- **Frontend**: Bridges Better Auth and FastAPI, handles UI

---

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Auth route group
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── api/auth/[...better-auth]/route.ts  # Better Auth API handler
│   ├── dashboard/
│   │   ├── layout.tsx            # Dashboard layout with sidebar
│   │   ├── page.tsx              # Dashboard home (stats)
│   │   └── todos/
│   │       ├── page.tsx          # Todo list
│   │       └── [id]/
│   │           ├── page.tsx      # Todo detail
│   │           └── not-found.tsx
│   ├── layout.tsx                # Root layout
│   ├── page.tsx                  # Landing page
│   ├── loading.tsx               # Global loading
│   ├── not-found.tsx             # 404 page
│   └── globals.css               # Tailwind styles
│
├── actions/                      # Server Actions
│   ├── auth.actions.ts           # getSession, requireAuth
│   └── todo.actions.ts           # createTodo, toggleTodo, deleteTodo
│
├── components/
│   ├── auth/                     # Auth components
│   │   ├── AuthCard.tsx
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── dashboard/                # Dashboard components
│   │   ├── AppSidebar.tsx        # Main sidebar (shadcn)
│   │   └── UserProfile.tsx       # User profile in sidebar
│   ├── landing/                  # Landing page components
│   │   ├── CTASection.tsx
│   │   ├── FeatureCard.tsx
│   │   ├── FeaturesGrid.tsx
│   │   └── Hero.tsx
│   ├── shared/                   # Shared components
│   │   ├── ErrorBoundary.tsx
│   │   ├── Footer.tsx
│   │   └── Header.tsx
│   ├── todos/                    # Todo components
│   │   ├── TodoDetail.tsx
│   │   ├── TodoItem.tsx
│   │   └── TodoList.tsx
│   └── ui/                       # shadcn/ui primitives
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
│   ├── use-mobile.ts             # Mobile detection (used by sidebar)
│   ├── use-stats.ts              # SWR hook for todo stats
│   └── use-todos.ts              # SWR hook for todos
│
├── lib/                          # Utilities & core logic
│   ├── api-client.ts             # FastAPI client (apiRequest, api.get/post/patch/delete)
│   ├── auth.ts                   # Better Auth server config (pg driver)
│   ├── auth-client.ts            # Better Auth client (signIn, signUp, signOut, useSession)
│   ├── backend-jwt.ts            # JWT issuer for FastAPI (issueBackendJwt)
│   ├── constants.ts              # Theme constants
│   ├── db.ts                     # Postgres pool (pg)
│   ├── types.ts                  # Shared TypeScript types
│   ├── utils.ts                  # cn() utility
│   └── validations/              # Zod schemas
│       ├── auth.schema.ts        # loginSchema, registerSchema
│       └── todo.schema.ts        # todoSchema, createTodoSchema
│
├── middleware.ts                 # Route protection
├── next.config.ts
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── CLAUDE.md                     # This file
```

---

## Core Patterns

### 1. Authentication Flow

**Better Auth Server Config** (`lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth"
import { Pool } from "pg"
import { jwt } from "better-auth/plugins"

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
})

export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
  database: pool,
  emailAndPassword: { enabled: true },
  plugins: [jwt()],
})
```

**Better Auth Client** (`lib/auth-client.ts`):
```typescript
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL,
})

export const { signIn, signUp, signOut, useSession } = authClient
```

**JWT Bridge for FastAPI** (`lib/backend-jwt.ts`):
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

### 2. Route Protection

**Middleware** (`middleware.ts`):
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { getSessionCookie } from 'better-auth/cookies'

export function middleware(request: NextRequest) {
  const sessionCookie = getSessionCookie(request)
  const { pathname } = request.nextUrl

  // Redirect authenticated users from login/register
  if (sessionCookie && ['/login', '/register'].includes(pathname)) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // Protect dashboard routes
  if (!sessionCookie && pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  return NextResponse.next()
}
```

**Server Action Auth** (`actions/auth.actions.ts`):
```typescript
"use server"
import { auth } from "@/lib/auth"
import { headers } from "next/headers"
import { redirect } from "next/navigation"

export async function getSession() {
  return await auth.api.getSession({ headers: await headers() })
}

export async function requireAuth() {
  const session = await getSession()
  if (!session) redirect('/login')
  return session
}
```

### 3. Server Actions for Todo CRUD

**Todo Actions** (`actions/todo.actions.ts`):
```typescript
"use server"
import { requireAuth } from "@/actions/auth.actions"
import { issueBackendJwt } from "@/lib/backend-jwt"
import { revalidatePath } from 'next/cache'

export async function createTodoAction(formData: FormData) {
  const session = await requireAuth()
  const userId = session?.user?.id
  const token = await issueBackendJwt(userId)

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/todos`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title, description, priority }),
  })

  revalidatePath('/dashboard/todos')
  revalidatePath('/dashboard')
  return response.json()
}
```

### 4. Client-Side Data Fetching (SWR)

**useTodos Hook** (`hooks/use-todos.ts`):
```typescript
import useSWR from 'swr'
import { api } from '@/lib/api-client'
import type { Todo } from '@/lib/types'

export function useTodos() {
  const { data, error, mutate, isLoading } = useSWR<Todo[]>(
    '/todos',
    (url: string) => api.get<Todo[]>(url),
    { revalidateOnFocus: true, revalidateOnReconnect: true }
  )
  return { todos: data, isLoading, error, mutate }
}
```

### 5. Optimistic Updates (React 19)

**TodoItem with useOptimistic** (`components/todos/TodoItem.tsx`):
```typescript
"use client"
import { startTransition, useOptimistic } from "react"

export function TodoItem({ todo }: TodoItemProps) {
  const [optimisticTodo, setOptimisticTodo] = useOptimistic(
    todo,
    (current, completed: boolean) => ({ ...current, completed })
  )

  const handleToggle = async () => {
    startTransition(() => setOptimisticTodo(!optimisticTodo.completed))
    await toggleTodoAction(todo.id, !optimisticTodo.completed)
  }
}
```

---

## Component Architecture

### Server Components (Default)
- No `'use client'` directive
- Can fetch data directly
- Used for: layouts, pages, static components

### Client Components
Only when you need:
- Event handlers (`onClick`, `onChange`)
- Browser APIs (`localStorage`, `window`)
- State (`useState`, `useReducer`)
- Hooks (`useRouter`, `useSession`)

**Mark with:**
```typescript
'use client'  // Must be at TOP of file
```

---

## Type Definitions

**Shared Types** (`lib/types.ts`):
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

**Zod Validation** (`lib/validations/todo.schema.ts`):
```typescript
import { z } from "zod"

export const createTodoSchema = z.object({
  title: z.string().min(1).max(100),
  description: z.string().optional(),
  priority: z.enum(["LOW", "MEDIUM", "HIGH"]).default("MEDIUM"),
})
```

---

## Styling

### Tailwind CSS + shadcn/ui
- Use `cn()` utility from `lib/utils.ts` for class merging
- shadcn/ui components in `components/ui/`
- Custom colors defined in `lib/constants.ts` and `tailwind.config.ts`

**Theme Colors:**
- `primary`: #f4252f (red)
- `obsidian`: #050505 (background)
- `charcoal`: #121212 (cards)
- `border-subtle`: #2a2a2a
- `border-sharp`: #444444

---

## Environment Variables

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

---

## Dependencies

```json
{
  "dependencies": {
    "@hookform/resolvers": "^5.2.2",
    "@radix-ui/react-*": "various",
    "@types/pg": "^8.16.0",
    "better-auth": "^1.4.10",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "jose": "^5.9.0",
    "lucide-react": "^0.562.0",
    "next": "16.1.1",
    "pg": "^8.16.3",
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "react-hook-form": "^7.69.0",
    "sonner": "^2.0.7",
    "swr": "^2.3.8",
    "tailwind-merge": "^3.4.0",
    "zod": "^4.3.4",
    "zustand": "^5.0.9"
  }
}
```

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `lib/auth.ts` | Better Auth server config (uses `pg` directly) |
| `lib/auth-client.ts` | Better Auth client exports |
| `lib/backend-jwt.ts` | JWT issuer for FastAPI communication |
| `lib/api-client.ts` | FastAPI HTTP client |
| `lib/types.ts` | Shared TypeScript interfaces |
| `actions/auth.actions.ts` | Server actions for auth |
| `actions/todo.actions.ts` | Server actions for todo CRUD |
| `middleware.ts` | Route protection |
| `app/dashboard/layout.tsx` | Dashboard layout with AppSidebar |

---

## Development Guidelines

### Type Safety
- No `any` types - use proper interfaces
- Use `z.infer<>` for Zod schema types
- User ID is `string` (Better Auth UUIDs)

### Naming Conventions
- Components: `PascalCase.tsx`
- Utilities: `kebab-case.ts`
- Hooks: `use-*.ts` or `use*.ts`
- Actions: `*.actions.ts`
- Schemas: `*.schema.ts`

### Performance
- 80%+ Server Components
- Use `Suspense` for streaming
- Use `revalidatePath` after mutations
- Use SWR for client-side caching

### Security
- Never expose `BETTER_AUTH_SECRET` to client
- Always use `requireAuth()` in protected routes
- JWT tokens are short-lived (1 hour)

---

## Running the Frontend

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```
