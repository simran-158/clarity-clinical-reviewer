import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from .ai import AIProvider
from .config import Settings
from .db import Database
from .errors import AppError
from .jobs import JobWorker
from .routes import router


class RequestGuard:
    """Bound body size before multipart parsing; enforce same-origin browser writes."""

    def __init__(self, app, settings):
        self.app, self.settings = app, settings

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))

        async def reject(status, code, message):
            await JSONResponse(
                {"error": {"code": code, "message": message}}, status_code=status
            )(scope, receive, send)

        if scope["method"] == "POST":
            origin = headers.get(b"origin", b"").decode()
            allowed = {self.settings.app_origin}
            if self.settings.environment != "production":
                allowed.update(
                    {
                        "http://127.0.0.1:5173",
                        "http://localhost:5173",
                        "http://localhost:8000",
                    }
                )
            if origin and origin not in allowed:
                return await reject(
                    403,
                    "invalid_origin",
                    "This request came from an unapproved origin.",
                )
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > 11 * 1024 * 1024:
                    return await reject(
                        413, "too_large", "Upload a file smaller than 10 MB."
                    )
                if not message.get("more_body", False):
                    break
            consumed = False
            original_receive = receive

            async def buffered_receive():
                nonlocal consumed
                if not consumed:
                    consumed = True
                    return {
                        "type": "http.request",
                        "body": bytes(body),
                        "more_body": False,
                    }
                return await original_receive()

            receive = buffered_receive

        async def secure_send(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(
                    [
                        (b"x-content-type-options", b"nosniff"),
                        (b"referrer-policy", b"no-referrer"),
                        (b"x-frame-options", b"DENY"),
                        (b"cache-control", b"no-store"),
                        (
                            b"content-security-policy",
                            b"default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; font-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'",
                        ),
                    ]
                )
            await send(message)

        await self.app(scope, receive, secure_send)


def create_app(settings=None, provider=None):
    settings = settings or Settings()
    db = Database(settings.database_url)
    provider = provider or AIProvider(settings)
    worker = JobWorker(db, provider, settings)

    @asynccontextmanager
    async def lifespan(app):
        settings.upload_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
        config.attributes["database_url"] = settings.database_url
        command.upgrade(config, "head")
        worker.recover()
        task = asyncio.create_task(worker.run())
        try:
            yield
        finally:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
            db.engine.dispose()

    app = FastAPI(
        title="Clarity Clinical Document Reviewer", version="1.0.0", lifespan=lifespan
    )
    app.state.settings = settings
    app.state.db = db
    app.state.provider = provider
    app.state.worker = worker
    app.state.submit_lock = asyncio.Lock()
    app.add_middleware(RequestGuard, settings=settings)

    @app.exception_handler(AppError)
    async def app_error(request, exc):
        return JSONResponse(
            {"error": {"code": exc.code, "message": exc.message}},
            status_code=exc.status,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(
            {
                "error": {
                    "code": "invalid_request",
                    "message": "Check your input and try again.",
                }
            },
            status_code=422,
        )

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return JSONResponse(
            {"error": {"code": "request_error", "message": str(exc.detail)}},
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        return JSONResponse(
            {
                "error": {
                    "code": "server_error",
                    "message": "The service could not complete this request. Please retry.",
                }
            },
            status_code=500,
        )

    app.include_router(router)
    if (settings.frontend_dir / "assets").exists():
        app.mount(
            "/assets",
            StaticFiles(directory=settings.frontend_dir / "assets"),
            name="assets",
        )

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if (
            path == "api"
            or path.startswith("api/")
            or "." in path
            or not (settings.frontend_dir / "index.html").exists()
        ):
            raise AppError(404, "not_found", "This page was not found.")
        return FileResponse(settings.frontend_dir / "index.html")

    return app


app = create_app()
