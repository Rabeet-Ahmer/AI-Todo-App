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
│   ├── __init__.py
│   ├── main.py              # FastAPI app, CORS, exception handlers
│   ├── config.py            # Pydantic settings (DB, JWT config)
│   ├── models/              # SQLModel (Database layer)
│   │   ├── __init__.py
│   │   ├── user.py          # Better Auth's users table (read-only)
│   │   └── todo.py          # Todos table (owned by FastAPI)
│   ├── schemas/             # Pydantic (API contracts)
│   │   ├── __init__.py
│   │   ├── todo.py          # TodoCreate, TodoUpdate, TodoResponse, TodoStats
│   │   └── common.py        # ErrorResponse, PaginationParams
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── deps.py          # get_current_user, get_session dependencies
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py    # Main v1 router
│   │       ├── todos.py     # Todo CRUD endpoints
│   │       ├── stats.py     # Todo statistics endpoint
│   │       └── auth.py      # /auth/me endpoint
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   └── todo_service.py  # Todo CRUD operations
│   ├── core/                # Utilities
│   │   ├── __init__.py
│   │   ├── security.py      # JWT validation (verify_token, extract_user_id_from_token)
│   │   └── exceptions.py    # Custom exceptions + handlers
│   └── db/
│       ├── __init__.py
│       └── session.py       # Async DB session factory (Neon)
├── pyproject.toml           # UV dependencies
├── uv.lock
├── .env                     # Environment variables (gitignored)
├── .python-version          # Python 3.13
├── CLAUDE.md                # This file
└── README.md
```

### 2. Database Models

**User Model** (app/models/user.py) - **READ-ONLY**, owned by Better Auth:
```python
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # String UUID from Better Auth
    email: str = Field(index=True, unique=True, max_length=255)
    name: Optional[str] = Field(default=None, max_length=255)
    image: Optional[str] = Field(default=None)
    email_verified: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime
    todos: List["Todo"] = Relationship(back_populates="user")
```

**Todo Model** (app/models/todo.py) - **FastAPI owns this**:
```python
class Todo(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    title: str = Field(index=True, max_length=200)
    description: Optional[str] = Field(max_length=1000)
    completed: bool = Field(default=False, sa_column=Column("is_completed", Boolean))
    priority: str = Field(default="MEDIUM")  # LOW, MEDIUM, HIGH
    created_at: datetime
    updated_at: datetime
    user_id: str = Field(foreign_key="user.id", index=True)
    user: "User" = Relationship(back_populates="todos")
```

**Key Notes:**
- User ID is `string` (Better Auth generates UUIDs)
- Todo `completed` maps to DB column `is_completed`
- Priority values: LOW, MEDIUM, HIGH

### 3. Authentication Flow

**JWT Validation** (app/api/deps.py):
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

**Security Configuration** (app/core/security.py):
```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
```

### 4. API Endpoints

**Routes** (app/api/v1/router.py):
```python
router.include_router(auth.router)    # /auth/me
router.include_router(todos.router)   # /todos (CRUD)
router.include_router(stats.router)   # /users/me/todos/stats
```

**Todo Endpoints** (app/api/v1/todos.py):
- `GET /api/v1/todos` - List user's todos
- `POST /api/v1/todos` - Create todo (201)
- `PATCH /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo (204)

**Stats Endpoint** (app/api/v1/stats.py):
- `GET /api/v1/users/me/todos/stats` - Get todo statistics (total, pending, completed)

**Auth Endpoint** (app/api/v1/auth.py):
- `GET /api/v1/auth/me` - Get current user profile

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
class TodoNotFoundException(TodoException):    # 404
class TodoAccessDeniedException(TodoException): # 403
class UserNotFoundException(TodoException):     # 404 (user_id: str)
class UnauthorizedException(TodoException):     # 401
class ValidationException(TodoException):       # 422
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
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
```

### 9. Main Application

**FastAPI App** (app/main.py):
```python
app = FastAPI(
    title="Todo Web App API",
    description="Backend API for Todo Web App with Better Auth integration",
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
    "alembic>=1.17.2",
    "asyncpg>=0.31.0",
    "fastapi[standard]>=0.128.0",
    "pydantic-settings>=2.12.0",
    "python-jose[cryptography]>=3.5.0",
    "sqlmodel>=0.0.31",
]
```

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
