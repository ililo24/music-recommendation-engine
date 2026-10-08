"""In-memory LRU cache for deserialized model artifacts.

Artifacts are immutable once written (they are versioned per tenant and
dataset), so caching by ``(tenant_id, model_version_id)`` is safe. The cache
is per-process — each server/worker process holds its own copy, bounded by
``model_cache_max_size`` from config.

Artifacts are only ever deserialized from bytes read through the storage
interface for keys recorded in the database (``ModelVersion.storage_key``) —
never from user-supplied files (CONVENTIONS.md rule 4).
"""

import io
import threading
from collections import OrderedDict
from uuid import UUID

import joblib

from musicrec.storage.base import Storage


class ModelCache:
    """Thread-safe LRU cache for deserialized model artifacts."""

    def __init__(self, storage: Storage, max_size: int = 10) -> None:
        """Create a cache backed by ``storage``, holding at most ``max_size`` models."""
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        self._storage = storage
        self._max_size = max_size
        self._entries: OrderedDict[tuple[UUID, UUID], object] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, tenant_id: UUID, version_id: UUID, storage_key: str) -> object:
        """Return the deserialized model for a version, loading it on a miss.

        Raises ``FileNotFoundError`` when the artifact is missing from storage.
        """
        key = (tenant_id, version_id)
        with self._lock:
            if key in self._entries:
                self._entries.move_to_end(key)
                return self._entries[key]

        # Load outside the lock so concurrent misses do not serialize; the
        # last insert wins and both callers receive a valid model.
        payload = self._storage.read(tenant_id, storage_key)
        model = joblib.load(io.BytesIO(payload))

        with self._lock:
            self._entries[key] = model
            while len(self._entries) > self._max_size:
                self._entries.popitem(last=False)
        return model

    def invalidate(self, tenant_id: UUID, version_id: UUID) -> None:
        """Drop a cached model (e.g. after a version is deactivated)."""
        with self._lock:
            self._entries.pop((tenant_id, version_id), None)

    def clear(self) -> None:
        """Drop every cached model."""
        with self._lock:
            self._entries.clear()
