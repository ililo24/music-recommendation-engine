# Multi-stage build for the musicrec FastAPI service.
#
# Stage 1 (builder) installs the package and its dependencies into a clean
# virtualenv. Stage 2 (runtime) copies only that virtualenv onto a fresh
# slim base image and runs the API as an unprivileged user.
#
# NOTE: the image installs from pyproject.toml (the canonical dependency
# list for the SaaS app), not requirements.txt, which carries legacy and
# notebook dependencies (jupyter, matplotlib, flask, pytest, ...).

# ------------------------------------------------------------------ builder
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Compilers in case a dependency ships no wheel for this platform.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Isolated environment that gets copied wholesale into the runtime stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# Install the package (and its dependencies) from pyproject.toml.
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --upgrade pip \
    && pip install .

# ------------------------------------------------------------------ runtime
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Unprivileged runtime user.
RUN useradd --create-home --shell /usr/sbin/nologin appuser

# Only the built virtualenv is carried over: no compilers, no build tools,
# no source checkout.
COPY --from=builder /opt/venv /opt/venv

RUN mkdir -p /app && chown appuser:appuser /app
WORKDIR /app
USER appuser

EXPOSE 8000

# curl is not present in the slim image; use the stdlib for the healthcheck.
# The health endpoint is /api/v1/health: src/musicrec/main.py mounts the
# health router with app.include_router(health_router, prefix="/api/v1").
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health', timeout=5)" || exit 1

# The ASGI app object is musicrec.main:app (src/musicrec/main.py).
CMD ["uvicorn", "musicrec.main:app", "--host", "0.0.0.0", "--port", "8000"]
