"""
Custom exception handlers for the FastAPI application
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Dict, Any


class TodoException(HTTPException):
    """Base exception class for todo-related errors"""

    def __init__(self, status_code: int, detail: str, headers: Dict[str, Any] = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class TodoNotFoundException(TodoException):
    """Raised when a todo item is not found"""

    def __init__(self, todo_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )


class TodoAccessDeniedException(TodoException):
    """Raised when a user tries to access a todo they don't own"""

    def __init__(self, todo_id: int):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to access todo with ID {todo_id}"
        )


class UserNotFoundException(TodoException):
    """Raised when a user is not found"""

    def __init__(self, user_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )


class UnauthorizedException(TodoException):
    """Raised when authentication fails"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access",
            headers={"WWW-Authenticate": "Bearer"}
        )


class ValidationException(TodoException):
    """Raised when input validation fails"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


# Exception handler functions for FastAPI
async def todo_not_found_handler(request: Request, exc: TodoNotFoundException):
    """Handle TodoNotFoundException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def todo_access_denied_handler(request: Request, exc: TodoAccessDeniedException):
    """Handle TodoAccessDeniedException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    """Handle UserNotFoundException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    """Handle UnauthorizedException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle ValidationException"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# Register all exception handlers
def register_exception_handlers(app):
    """Register all custom exception handlers with the FastAPI app"""
    app.add_exception_handler(TodoNotFoundException, todo_not_found_handler)
    app.add_exception_handler(TodoAccessDeniedException, todo_access_denied_handler)
    app.add_exception_handler(UserNotFoundException, user_not_found_handler)
    app.add_exception_handler(UnauthorizedException, unauthorized_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)