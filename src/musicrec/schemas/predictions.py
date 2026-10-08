"""Request/response schemas for the predictions API."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator


class PredictItem(BaseModel):
    """One track to score: client-supplied feature values."""

    track_id: str | None = None
    features: dict[str, Any]


class PredictRequest(BaseModel):
    """Single prediction (top-level ``features``) or batch (``items``).

    Exactly one of the two shapes must be provided. The maximum batch size is
    enforced by the endpoint from config (rule 3), not here — schemas are
    static and cannot read settings.
    """

    track_id: str | None = None
    features: dict[str, Any] | None = None
    items: list[PredictItem] | None = None

    @model_validator(mode="after")
    def _exactly_one_shape(self) -> "PredictRequest":
        if (self.features is None) == (self.items is None):
            raise ValueError(
                "Provide either 'features' (single prediction) "
                "or 'items' (batch), not both"
            )
        return self


class PredictResult(BaseModel):
    """The score for one requested track."""

    track_id: str | None = None
    prediction: float


class PredictResponse(BaseModel):
    """One result per requested track, in request order (single = one result)."""

    model_version_id: UUID
    results: list[PredictResult]
