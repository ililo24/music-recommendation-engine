# 🎵 MelodyAI — Music Recommendation SaaS

A FastAPI-based music recommendation service (`musicrec`), refactored from the
original [music-recommendation-engine](https://github.com/ililo24/music-recommendation-engine).
The service scores user–track preference from listening behavior (completion
rates, stream counts, rewind behavior) and serves the scores over a validated
HTTP API. The original Flask web app and CLI are preserved, frozen, under
`legacy/`.

## 🏗️ Architecture

- **api** — FastAPI application (`src/musicrec`), served by uvicorn on port 8000.
  Pydantic schemas validate every request; model artifacts are loaded through a
  thread-safe LRU cache backed by multi-tenant storage. Health endpoint:
  `GET /api/v1/health`.
- **worker** — planned RQ (Redis Queue) workers for async jobs (model training,
  batch scoring), per the refactor plan in `src/musicrec/main.py`. The compose
  service is a documented placeholder until the module exists.
- **postgres** — PostgreSQL 16, provisioned by docker compose; reserved for
  tenant/model persistence (not yet read by the application).
- **redis** — Redis 7, provisioned by docker compose; reserved for the RQ task
  queue and cross-process rate limiting (not yet read by the application).

**Design rules** (see CONVENTIONS.md):

- `musicrec.ml` is pure ML — it never reads config; callers pass settings
  explicitly.
- All configuration comes from environment variables via pydantic-settings;
  nothing sensitive is hardcoded.
- Batch-size limits are enforced at the endpoint from config, not in schemas.

## ✨ Features

- **Preference scoring** from completion rates, stream counts, and rewind behavior
- **Feature engineering** — temporal, completion, categorical, and engagement features
- **Time-series aware** train/test splitting
- **Validated API** — single or batch prediction shapes, exactly one per request
- **Request-id tracing** — `X-Request-ID` propagated to responses and every log line
- **Thread-safe model cache** — LRU of deserialized artifacts, per process
- **Per-key rate limiting** — sliding window, configurable via environment
- **Structured JSON logging** with a plain-text fallback (`LOG_JSON=false`)
- **12-factor configuration** — everything from env vars or a local `.env`

## 📊 Model performance

**No performance numbers are claimed in this README.** Per repo policy
(CONVENTIONS.md rule 10), any metric quoted here must be reproducible from a
committed script (`scripts/benchmark.py`). Until that script and its output are
checked in, measure on your own data:

```bash
python legacy/train.py --data data/raw/listening_history.csv
```

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **API**: FastAPI, pydantic, pydantic-settings, uvicorn
- **ML**: pandas, numpy, scikit-learn, joblib
- **Infra**: Docker (multi-stage, non-root), docker compose, PostgreSQL 16, Redis 7
- **Quality**: ruff, black, mypy, pre-commit, pytest with a coverage gate, GitHub Actions

## 📁 Project Structure

```
├── .github/workflows/ci.yml   # CI: ruff, black, mypy, pytest (coverage gate)
├── src/musicrec/              # The SaaS application package
│   ├── api/v1/                # Routers (health, predictions, ...)
│   ├── core/                  # config.py (pydantic-settings), logging.py
│   ├── ml/                    # Pure ML: features, training, evaluation
│   ├── schemas/               # pydantic request/response models
│   ├── services/              # model cache, storage, visualization
│   └── main.py                # FastAPI app assembly
├── tests/                     # pytest suite (unit + integration)
├── legacy/                    # Frozen pre-SaaS code (Flask app, CLI, old config)
├── scripts/                   # (planned) benchmark.py and operational scripts
├── data/                      # Raw and processed data
├── models/                    # Trained model artifacts
├── Dockerfile                 # Multi-stage, non-root image for the API
├── docker-compose.yml         # api, worker, postgres, redis
├── .env.example               # Template for all environment variables
├── .pre-commit-config.yaml    # ruff, black, mypy, hygiene hooks
├── pyproject.toml             # Packaging + tool configuration
├── requirements.txt           # Legacy/notebook dependency pinning
└── run_tests.py               # Local test runner helper
```

## 🚀 Getting Started

### Run with Docker (recommended)

```bash
git clone https://github.com/ililo24/music-recommendation-engine.git
cd music-recommendation-engine

cp .env.example .env     # then set SECRET_KEY and POSTGRES_PASSWORD

docker compose up --build
```

- Interactive OpenAPI docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

> **Note on the worker service:** no worker module exists in the codebase yet,
> so the `worker` container exits with `ModuleNotFoundError` by design — it is
> included to document the target topology. Start everything else with
> `docker compose up --build postgres redis api`, or simply ignore the exited
> worker container.

### Local development

```bash
git clone https://github.com/ililo24/music-recommendation-engine.git
cd music-recommendation-engine

pip install -e ".[dev]"     # package + pytest/pytest-cov, ruff, black, mypy
cp .env.example .env
pre-commit install          # wire up the git hooks

uvicorn musicrec.main:app --reload   # API on http://localhost:8000
```

### Python API

```python
import pandas as pd
from musicrec.ml.features import apply_features, calculate_preference_score
from musicrec.ml.training import train_model, evaluate_model

df = pd.read_csv("data/raw/your_data.csv")
train_df, test_df = ...  # your split; time-based recommended (see legacy/train.py)

train_processed, test_processed = apply_features(train_df, test_df)
train_processed = calculate_preference_score(train_processed)

model = train_model(train_processed, test_processed)
metrics = evaluate_model(model, test_processed)
```

See the module docstrings in `src/musicrec/ml/` for the full signatures,
including `ModelEvaluator` for cross-validated performance analysis.

### Legacy web app & CLI

The original Flask interface (CSV upload, one-click training, metrics
dashboards) and the training CLI remain available as frozen code in `legacy/`:

```bash
python legacy/web_app.py                                            # Flask UI on :5000
python legacy/train.py --data data/raw/listening_history.csv        # train
python legacy/train.py --predict --model models/<model>.pkl --data data/raw/new_data.csv
```

## 🧪 Testing

```bash
# Full suite with coverage (same 80% gate as CI)
pytest --cov=musicrec --cov-report=term-missing --cov-fail-under=80

# Or the helper script
python run_tests.py --coverage
```

CI enforces a coverage gate: the build fails below **80%** coverage of the
`musicrec` package (`--cov-fail-under=80`).

## 🧹 Code Quality

| Tool       | Purpose         | Command                        |
|------------|-----------------|--------------------------------|
| ruff       | Linting         | `ruff check .`                 |
| black      | Formatting      | `black .`                      |
| mypy       | Type checking   | `mypy src/musicrec`            |
| pre-commit | Git hook runner | `pre-commit run --all-files`   |

Install the hooks once per clone:

```bash
pre-commit install
```

GitHub Actions (`.github/workflows/ci.yml`) runs ruff, black, mypy, and the
pytest coverage gate on every push to `main` and on every pull request.

## ⚙️ Configuration

All settings are read from environment variables (or a local `.env` file) by
`src/musicrec/core/config.py`. See `.env.example` for the full annotated list.
Highlights:

| Variable                    | Default              | Purpose                                 |
|-----------------------------|----------------------|-----------------------------------------|
| `SECRET_KEY`                | ⚠️ insecure default  | Signing secret — set a real one         |
| `MODEL_N_ESTIMATORS`        | 200                  | Random forest size                      |
| `MODEL_TEST_SPLIT`          | 0.2                  | Train/test split fraction               |
| `PREDICT_MAX_BATCH_SIZE`    | 100                  | Max items per batch prediction          |
| `MODEL_CACHE_MAX_SIZE`      | 10                   | LRU capacity for deserialized models    |
| `RATE_LIMIT_MAX_REQUESTS`   | 60                   | Requests per window per API key         |
| `RATE_LIMIT_WINDOW_SECONDS` | 60                   | Rate limit window length                |
| `LOG_JSON`                  | true                 | Structured JSON logs                    |

Legacy variable names (`LOG_FILE`, `TEST_SPLIT`) are still honored as aliases.

## 🗺️ Roadmap

- [ ] RQ worker service (task queue) + redis-backed rate limiting
- [ ] Persist tenants and model metadata in PostgreSQL
- [ ] `scripts/benchmark.py` — reproducible metrics that may be quoted in this README
- [ ] Auth phase: make `SECRET_KEY` required and drop the insecure default
- [ ] Spotify API integration
- [ ] Collaborative filtering
- [ ] API endpoints for mobile apps

## 🤝 Contributing

```bash
pip install -e ".[dev]"
pre-commit install
pytest --cov=musicrec
```

Keep `musicrec.ml` free of config reads — pass settings explicitly. Add or
update tests with your changes; CI gates on 80% coverage.

## 📄 License

MIT License - feel free to use for learning and projects.

## 👨‍💻 Author

**Ililo Altaye** - [GitHub](https://github.com/ililo24)

---

⭐ **Star this repo if you found it helpful**
