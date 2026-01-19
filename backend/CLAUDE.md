# Backend Development Rules

## Architecture Overview: Better Auth + FastAPI Hybrid

**This backend works in conjunction with Better Auth (Next.js/TypeScript):**

```
Next.js Frontend (Better Auth + UI)
        ↓
    ┌───────────────┐
    │  Better Auth  │ → JWT Generation, User/Session Management
    └───────────────┘
        ↓
    ┌───────────────┐
    │   FastAPI     │ → JWT Validation, Business Logic (Todos CRUD)
    └───────────────┘
        ↓
    ┌───────────────┐
    │  PostgreSQL   │ → users (Better Auth), todos (FastAPI)
    └───────────────┘
```

**Division of Responsibilities:**
- **Better Auth**: User registration, login, JWT generation, session management
- **FastAPI**: JWT validation, todo CRUD operations
- **Shared**: PostgreSQL database, JWT secret key

---

## Core Architecture Patterns

### 1. Project Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, exception handlers
│   ├── config.py            # Pydantic settings (DB, JWT config)
│   ├── models/              # SQLModel (Database layer)
│   │   ├── user.py          # Better Auth's users table (read-only)
│   │   └── todo.py          # Todos table (owned by FastAPI)
│   ├── schemas/             # Pydantic (API contracts)
│   │   ├── todo.py          # TodoCreate, TodoUpdate, TodoResponse
│   │   └── common.py        # Shared schemas
│   ├── api/v1/              # API routes
│   │   ├── router.py        # Main v1 router
│   │   ├── todos.py         # Todo CRUD endpoints
│   │   ├── stats.py         # Todo statistics endpoint
│   │   ├── auth.py          # /auth/me endpoint
│   │   └── deps.py          # get_current_user, get_session
│   ├── services/            # Business logic
│   │   └── todo_service.py  # Todo CRUD operations
│   ├── core/                # Utilities
│   │   ├── security.py      # JWT validation
│   │   └── exceptions.py    # Custom exceptions
│   └── db/
│       └── session.py       # Async DB session factory (Neon)
├── pyproject.toml           # UV dependencies
└── uv.lock
```

### 2. Database Models

**User Model** (app/models/user.py) - **READ-ONLY**, owned by Better Auth:
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # String ID from Better Auth
    email: str = Field(index=True, unique=True)
    name: Optional[str] = None
    email_verified: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime
    todos: List["Todo"] = Relationship(back_populates="user")
```

**Todo Model** (app/models/todo.py) - **FastAPI owns this**:
```python
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(max_length=1000)
    completed: bool = Field(default=False, sa_column=Column("is_completed", Boolean))
    priority: str = Field(default="MEDIUM")  # LOW, MEDIUM, HIGH
    created_at: datetime
    updated_at: datetime
    user_id: str = Field(foreign_key="user.id", index=True)  # FK to Better Auth
    user: "User" = Relationship(back_populates="todos")
```

**Key Notes:**
- User ID is `string` (Better Auth generates UUIDs)
- Todo `completed` maps to DB column `is_completed`
- Priority column: LOW/MEDIUM/HIGH

### 3. Authentication Flow

**JWT Validation** (app/api/v1/deps.py):
```python
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    # 1. Extract token from Authorization: Bearer <token>
    # 2. Decode using shared SECRET_KEY
    # 3. Extract user_id from payload["sub"]
    # 4. Query Better Auth's users table
    # 5. Return User object or raise 401
```

**Security Configuration** (app/core/security.py):
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
```

### 4. API Endpoints

**Routes** (app/api/v1/router.py):
```python
router.include_router(auth.router)    # /auth/me
router.include_router(todos.router)   # /todos (CRUD)
router.include_router(stats.router)   # /users/me/todos/stats
```

**Todo Endpoints** (app/api/v1/todos.py):
- `GET /todos` - List user's todos
- `POST /todos` - Create todo
- `PATCH /todos/{id}` - Update todo
- `DELETE /todos/{id}` - Delete todo

**Stats Endpoint** (app/api/v1/stats.py):
- `GET /users/me/todos/stats` - Get todo statistics (total, pending, completed)

**Auth Endpoint** (app/api/v1/auth.py):
- `GET /auth/me` - Get current user profile

### 5. Service Layer

**TodoService** (app/services/todo_service.py):
```python
class TodoService:
    @staticmethod
    async def create_todo(session, todo_in, user_id) -> Todo

    @staticmethod
    async def get_todos(session, user_id) -> Sequence[Todo]

    @staticmethod
    async def update_todo(session, todo_id, todo_in, user_id) -> Todo

    @staticmethod
    async def delete_todo(session, todo_id, user_id) -> bool

    @staticmethod
    async def get_stats(session, user_id) -> TodoStats
```

**Business Rules:**
- All methods enforce user ownership (todos filtered by `user_id`)
- Raise `TodoNotFoundException` if todo not found or unauthorized
- Use `model_dump(exclude_unset=True)` for partial updates

### 6. Database Session

**Async Session Factory** (app/db/session.py):
```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

engine = create_async_engine(
    DATABASE_URL,  # postgresql+asyncpg://...
    echo=False,
    pool_pre_ping=True,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
```

### 7. Exception Handling

**Custom Exceptions** (app/core/exceptions.py):
```python
class TodoNotFoundException(TodoException):  # 404
class TodoAccessDeniedException(TodoException):  # 403
class UnauthorizedException(TodoException):  # 401
class ValidationException(TodoException):  # 422
```

**Exception Handlers** (registered in main.py):
```python
register_exception_handlers(app)
```

### 8. Configuration

**Settings** (app/config.py):
```python
class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    class Config:
        env_file = ".env"
```

### 9. Main Application

**FastAPI App** (app/main.py):
```python
app = FastAPI(
    title="Todo Web App API",
    version="1.0.0",
)

# Register exception handlers
register_exception_handlers(app)

# CORS for Next.js frontend
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, ...)

# Include v1 router
app.include_router(router.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## Development Guidelines

### Type Safety
- Use `Annotated[Type, Depends()]` for dependencies
- No `Any` types allowed
- User ID is **string** type (not int)
- Use `Optional[T]` for nullable fields
- Pydantic v2: `ConfigDict(from_attributes=True)`

### Database Patterns
- Always use `async def` for I/O operations
- Use `select().where()` for queries
- Order by `created_at.desc()` for lists
- Filter by `user_id` for security
- Use `model_dump(exclude_unset=True)` for updates
- Use `func.count()` for aggregations

### API Patterns
- All routes require authentication (except /health)
- Return `Sequence[TodoResponse]` for lists
- Use `status_code=201` for POST
- Use `status_code=204` for DELETE
- Raise custom exceptions, not generic HTTPException

### Security Rules
- **NEVER** generate JWT tokens (Better Auth does this)
- **NEVER** create users (Better Auth does this)
- **ALWAYS** validate JWT on every request
- **ALWAYS** filter by user_id for authorization
- JWT secret **MUST** match Better Auth's secret

### Dependencies
```toml
[project]
dependencies = [
    "fastapi[standard]>=0.128.0",
    "sqlmodel>=0.0.31",
    "asyncpg>=0.31.0",           # Async PostgreSQL driver
    "python-jose[cryptography]",  # JWT validation
    "pydantic-settings>=2.12.0",
    "alembic>=1.17.2",           # Migrations
]
```

---

## Key Differences from CLAUDE.md Template

1. **User ID is string, not int** - Better Auth uses UUID strings
2. **Todo.completed maps to is_completed column** - Using `sa_column` mapping
3. **Priority field added** - LOW/MEDIUM/HIGH values
4. **Stats endpoint** - Dashboard statistics at `/users/me/todos/stats`
5. **No Alembic setup yet** - Using SQLModel table creation
6. **No password hashing** - Better Auth handles all auth

---

## Environment Variables (.env)

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

## Running the Backend

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Health check
curl http://localhost:8000/health
```

---

## API Testing Examples

```bash
# Get todos (requires auth)
curl -H "Authorization: Bearer <jwt>" http://localhost:8000/api/v1/todos

# Create todo
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "priority": "HIGH"}'

# Get stats
curl -H "Authorization: Bearer <jwt>" \
  http://localhost:8000/api/v1/users/me/todos/stats

# Get current user
curl -H "Authorization: Bearer <jwt>" \
  http://localhost:8000/api/v1/auth/me
```
