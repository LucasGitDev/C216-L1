import time
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Expose request processing time through a response header."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{elapsed:.6f}"
        return response
