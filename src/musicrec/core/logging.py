"""Structured JSON logging.

``configure_logging`` sets up the root logger once (JSON by default, plain
text when ``LOG_JSON=false``). ``request_id_ctx`` carries the per-request id
set by the request-context middleware in ``musicrec.main``; the JSON
formatter includes it in every log line emitted while that request is being
handled.
"""

import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import datetime, timezone

from musicrec.core.config import Settings

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)

# LogRecord attributes that are not user-provided ``extra`` fields.
_STANDARD_FIELDS = frozenset({
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "taskName", "message", "asctime",
})


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects.

    Includes the current request id (when set by the request-context
    middleware) and any user-provided ``extra`` fields.
    """

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = request_id_ctx.get()
        if request_id:
            entry["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key not in _STANDARD_FIELDS:
                entry[key] = value

        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(entry, default=str)


_configured = False


def configure_logging(settings: Settings) -> None:
    """Configure root logging. Idempotent: only the first call takes effect.

    JSON structured logging is the default; ``LOG_JSON=false`` switches to the
    plain-text ``log_format`` from settings. Third-party loggers are silenced
    so they do not pollute the structured output (uvicorn's own access log is
    replaced by the request-context middleware's structured log line).
    """
    global _configured
    if _configured:
        return
    _configured = True

    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())

    if settings.log_file_path:
        os.makedirs(os.path.dirname(settings.log_file_path) or ".", exist_ok=True)
        handler: logging.Handler = logging.FileHandler(settings.log_file_path)
    else:
        handler = logging.StreamHandler(sys.stdout)

    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(settings.log_format))

    root.addHandler(handler)

    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("seaborn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a logger in the application namespace."""
    return logging.getLogger(name)
