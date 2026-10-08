"""Application exception hierarchy.

Every exception carries an HTTP status code, a stable machine-readable
``code``, and a human-readable default ``message`` so the global exception
handlers (``musicrec.main``) can return the consistent error schema from
``musicrec.schemas.errors``.
"""

from typing import Any


class MusicRecError(Exception):
    """Base class for all application errors."""

    status_code: int = 500
    code: str = "internal_error"
    message: str = "Internal server error"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message or self.message)
        self.details: dict[str, Any] = details or {}


class NotFoundError(MusicRecError):
    """Requested resource does not exist."""

    status_code = 404
    code = "not_found"
    message = "Resource not found"


class InvalidInputError(MusicRecError):
    """Domain-level input validation failure."""

    status_code = 422
    code = "invalid_input"
    message = "Invalid input"


class ConflictError(MusicRecError):
    """Request conflicts with the current state."""

    status_code = 409
    code = "conflict"
    message = "Resource conflict"
