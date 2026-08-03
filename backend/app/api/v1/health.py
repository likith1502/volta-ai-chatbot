from fastapi import APIRouter
from app.config.constants import HEALTH_STATUS_OK
from app.config.settings import settings
from app.utils.responses import success_response

router = APIRouter()


@router.get("", summary="V1 Health Check", description="Foundation API health check endpoint.")
@router.get("/", include_in_schema=False)
def get_v1_health():
    health_data = {
        "status": HEALTH_STATUS_OK,
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
    return success_response(
        data=health_data,
        message="V1 Health check successful",
    )
