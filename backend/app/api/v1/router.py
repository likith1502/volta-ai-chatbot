from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.routers.bookings import router as bookings_router
from app.api.v1.routers.chat import router as chat_router
from app.api.v1.routers.conversations import router as conversations_router
from app.api.v1.routers.notifications import router as notifications_router
from app.api.v1.routers.recommendations import router as recommendations_router
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
