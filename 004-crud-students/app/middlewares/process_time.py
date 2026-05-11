import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class ProcessTimeMiddleware:
    """Expose request processing time via the `X-Process-Time` response header.

    Implemented as a pure ASGI middleware so it does not run handlers in a
    separate task — this keeps FastAPI dependency cleanup (e.g. asyncpg pool
    connection release) on the same task that acquired the resource.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                elapsed = time.perf_counter() - start_time
                headers = list(message.get("headers", []))
                headers.append(
                    (b"x-process-time", f"{elapsed:.6f}".encode("latin-1"))
                )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_header)
