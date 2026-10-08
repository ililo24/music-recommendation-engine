"""FastAPI application factory.

Phase 0 of the SaaS refactor: app factory, ``/api/v1/health``, structured
JSON logging, consistent error responses, and CORS from config. No auth or
database yet — later phases add auth/db dependencies in ``api/deps``, the
remaining v1 routers, and the RQ workers.
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from musicrec.api.v1.health import router as health_router
from musicrec.core.config import Settings, get_settings
from musicrec.core.exceptions import MusicRecError
from musicrec.core.logging import configure_logging, get_logger, request_id_ctx
from musicrec.schemas.errors import ErrorDetail, ErrorResponse

logger = get_logger(__name__)

# Stable error codes for HTTP exceptions raised outside our own handlers.
_HTTP_ERROR_CODES = {
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
}


class RequestContextMiddleware:
    """Pure ASGI middleware that assigns a request id and logs each request.

    - Reuses an incoming ``X-Request-ID`` header or generates one, and exposes
      it to the app (request headers), to the structured logging context, and
      on the ``X-Request-ID`` response header.
    - Emits one structured log line per request with method, path, status and
      duration.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = MutableHeaders(scope=scope)
        request_id = headers.get("x-request-id") or uuid.uuid4().hex
        # Make the id visible to the app and to the error handlers via the
        # request headers, and to the log formatter via the context var.
        headers["x-request-id"] = request_id
        token = request_id_ctx.set(request_id)
        start = time.perf_counter()
        status_code: int | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
                MutableHeaders(scope=message)["x-request-id"] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            get_logger("musicrec.access").info(
                "request completed",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            request_id_ctx.reset(token)


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict | None = None,
) -> JSONResponse:
    """Build the consistent error envelope (see ``schemas/errors.py``)."""
    request_id = request_id_ctx.get() or request.headers.get("x-request-id")
    body = ErrorResponse(
        error=ErrorDetail(code=code, message=message, details=jsonable_encoder(details)),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
        headers={"X-Request-ID": request_id} if request_id else None,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Map every failure mode onto the consistent error schema."""

    @app.exception_handler(MusicRecError)
    async def handle_app_error(request: Request, exc: MusicRecError) -> JSONResponse:
        level = logging.ERROR if exc.status_code >= 500 else logging.WARNING
        logger.log(level, "application error", extra={"code": exc.code, "status_code": exc.status_code})
        return _error_response(request, exc.status_code, exc.code, str(exc), exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("request validation failed")
        return _error_response(
            request,
            422,
            "validation_error",
            "Request validation failed",
            {"errors": jsonable_encoder(exc.errors())},
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _HTTP_ERROR_CODES.get(exc.status_code, "http_error")
        return _error_response(request, exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled exception")
        return _error_response(request, 500, "internal_error", "Internal server error")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )

    # CORS from config (rule 3: nothing hardcoded).
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allowed_origins,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allowed_methods,
            allow_headers=settings.cors_allowed_headers,
        )

    # Request ids + structured request logging (outermost user middleware, so
    # preflights are logged too).
    app.add_middleware(RequestContextMiddleware)

    # Consistent error responses for every failure mode.
    register_exception_handlers(app)

    # Routers.
    app.include_router(health_router, prefix="/api/v1")

    return app


app = create_app()
