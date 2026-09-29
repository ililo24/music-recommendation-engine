# Project: Music Recommendation SaaS (refactor of music-recommendation-engine)

## Goal
Turn a single-user Flask/CSV/sklearn tool into a multi-tenant SaaS API where
each customer uploads listening data, trains a private model, and gets
preference scores/recommendations via API + dashboard.

## Target stack (do not substitute)
- Python 3.11+, FastAPI, Pydantic v2, pydantic-settings
- PostgreSQL + SQLAlchemy 2.0 + Alembic (SQLite only for tests)
- Background jobs: RQ + Redis (training must NEVER run in a request handler)
- Auth: JWT (access + refresh), password hashing with argon2/bcrypt, API keys for programmatic access
- Model artifacts: stored via a storage interface (local disk impl now, S3 impl later), never in git
- Billing: Stripe (added in a later phase, behind a feature flag)
- Tooling: ruff, black, mypy, pytest, pre-commit, Docker + docker-compose, GitHub Actions

## Target structure
```
src/musicrec/
  core/          # config.py, logging.py, security.py, exceptions.py
  ml/            # features.py, training.py, evaluation.py, inference.py (PURE functions, no Flask/FastAPI/DB imports)
  db/            # models.py, session.py, repositories.py
  schemas/       # Pydantic request/response models
  services/      # business logic: datasets, training_jobs, predictions, billing
  storage/       # base.py (interface), local.py
  api/
    deps.py
    v1/          # routers: auth, datasets, models, predictions, billing, health
  workers/       # RQ tasks
  main.py        # FastAPI app factory
alembic/
tests/{unit,integration}/
frontend/        # optional, later
docker/ , docker-compose.yml, .github/workflows/ci.yml
```

## Hard rules
1. `ml/` must be framework-agnostic and stateless: no globals, no file paths, no DB. Inputs are DataFrames/params, outputs are DataFrames/models/metrics.
2. Every DB row and every stored file is scoped to a `tenant_id` (or `user_id`). Every query goes through a repository that requires it. No unscoped queries.
3. No secrets, paths, or thresholds hardcoded. Everything via `core/config.py` (env vars).
4. Uploaded CSVs are untrusted: validate schema, size limit, row limit, dtypes. Never `pickle.load` a file a user uploaded.
5. Model artifacts are versioned per tenant: (tenant_id, model_id, version) with metrics stored in DB.
6. Type hints on all public functions; docstrings on services and routers.
7. Preserve existing ML behavior. Any change to feature logic needs a regression test first.
8. Small, reviewable changes. If a task needs >10 files changed, stop and propose a split.
9. Do not delete legacy code until its replacement has passing tests; move it to `legacy/` first.
10. Never fabricate metrics. README performance claims must come from a reproducible script.
