from fastapi import APIRouter
from app.api.v1 import auth, todos, stats, chat

router = APIRouter()
router.include_router(auth.router)
router.include_router(todos.router)
router.include_router(stats.router)
router.include_router(chat.router)
