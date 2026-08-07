from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.routers.agents import router as agents_router
from app.api.v1.routers.bookings import router as bookings_router
from app.api.v1.routers.chat import router as chat_router
from app.api.v1.routers.conversations import router as conversations_router
from app.api.v1.routers.graph_runtime import router as graph_runtime_router
from app.api.v1.routers.memory import router as memory_router
from app.api.v1.routers.notifications import router as notifications_router
from app.api.v1.routers.prompts import router as prompts_router
from app.api.v1.routers.rag import router as rag_router
from app.api.v1.routers.recommendations import router as recommendations_router
from app.api.v1.routers.runtime import router as runtime_router
from app.api.v1.routers.tools import router as tools_router
from app.api.v1.routers.users import router as users_router

api_v1_router = APIRouter()

# Register V1 Sub-Routers
api_v1_router.include_router(health_router, prefix="/health", tags=["Health"])
api_v1_router.include_router(users_router)
api_v1_router.include_router(conversations_router)
api_v1_router.include_router(recommendations_router)
api_v1_router.include_router(bookings_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(runtime_router)
api_v1_router.include_router(prompts_router)
api_v1_router.include_router(memory_router)
api_v1_router.include_router(tools_router)
api_v1_router.include_router(graph_runtime_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(rag_router)
