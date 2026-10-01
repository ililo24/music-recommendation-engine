"""Consistent error response schema.

Every error response (domain errors, request validation failures, HTTP
exceptions, unhandled exceptions) uses this envelope, produced by the global
exception handlers in ``musicrec.main``.
"""

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Machine-readable error information."""

    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Envelope for every error response."""

    error: ErrorDetail
    request_id: str | None = None
