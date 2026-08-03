from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.health import get_v1_health
from app.api.v1.router import api_v1_router
from app.config.settings import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import logger, setup_logging
from app.utils.responses import success_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})")
    yield
    # Shutdown phase
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Configuration
allow_credentials = "*" not in settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

# Include API Routers
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)


# Root Endpoint
@app.get("/", summary="Root Endpoint", tags=["Root"])
def read_root():
    return success_response(
        data={
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
        },
        message="VOLTA AI Chatbot backend is running",
    )


# Top-Level Health Endpoint
@app.get("/health", summary="Top-Level Health Check", tags=["Health"])
def top_level_health():
    return get_v1_health()
