from fastapi import FastAPI

from app.middlewares.process_time import ProcessTimeMiddleware


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(ProcessTimeMiddleware)
