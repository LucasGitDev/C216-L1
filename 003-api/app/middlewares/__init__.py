from fastapi import FastAPI

from app.middlewares.process_time import ProcessTimeMiddleware


def register_middlewares(app: FastAPI) -> None:
    """Register all application middlewares in a single place."""

    app.add_middleware(ProcessTimeMiddleware)
