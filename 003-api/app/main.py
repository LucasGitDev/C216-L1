from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.middlewares import register_middlewares


def create_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version=settings.app_version,
    )
    register_middlewares(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
