"""Application configuration.

pydantic-settings based configuration (CONVENTION.md rule 3): every setting
comes from an environment variable or a local ``.env`` file; nothing
sensitive is hardcoded. This module replaces the legacy JSON-file config
(``src/config.py``, now moved to ``legacy/``).

Legacy environment variable names that differ from the field names
(``LOG_FILE``, ``TEST_SPLIT``) are still honored via aliases so existing
deployments keep working.
"""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central, environment-driven application settings.

    Values are read from case-insensitive environment variables and from a
    local ``.env`` file when present. Unknown environment variables are
    ignored so leftover legacy variables cannot break startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_name: str = "musicrec"
    environment: str = "development"
    debug: bool = False

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: str | None = Field(
        default=None,
        validation_alias=AliasChoices("log_file_path", "log_file"),
    )

    # ------------------------------------------------------------------
    # Legacy Flask web app (removed together with legacy/web_app.py)
    # ------------------------------------------------------------------
    web_host: str = "0.0.0.0"
    web_port: int = 5000
    web_debug: bool = False
    # TODO(auth phase): remove the insecure default and make this required.
    secret_key: str = "change-this-in-production"

    # ------------------------------------------------------------------
    # Model defaults. These are passed into ``musicrec.ml`` functions as
    # explicit arguments; ``ml/`` itself never reads config (rule 1).
    # ------------------------------------------------------------------
    model_n_estimators: int = 200
    model_random_state: int = 42
    model_test_split: float = Field(
        default=0.2,
        validation_alias=AliasChoices("model_test_split", "test_split"),
    )
    model_cv_folds: int = 5
    feature_weights: tuple[float, float] = (0.6, 0.7)

    # ------------------------------------------------------------------
    # Data limits (upload validation, rule 4)
    # ------------------------------------------------------------------
    max_memory_usage_mb: int = 1000


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()
