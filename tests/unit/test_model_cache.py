"""Unit tests for the model cache (fake storage, no real artifacts)."""

import io
import uuid

import joblib
import pytest

from musicrec.services.model_cache import ModelCache
from musicrec.storage.base import Storage


class FakeStorage(Storage):
    """In-memory storage double."""

    def __init__(self) -> None:
        self.files: dict[tuple[str, str], bytes] = {}
        self.reads = 0

    def save(self, tenant_id, key, data):
        self.files[(str(tenant_id), key)] = data
        return key

    def read(self, tenant_id, key):
        self.reads += 1
        try:
            return self.files[(str(tenant_id), key)]
        except KeyError:
            raise FileNotFoundError(key)

    def delete(self, tenant_id, key):
        self.files.pop((str(tenant_id), key), None)

    def exists(self, tenant_id, key):
        return (str(tenant_id), key) in self.files


def _seed(storage: FakeStorage, tenant_id, version_id, key="models/v1.joblib", payload=None):
    """Write a joblib-serialized artifact into the fake storage."""
    buf = io.BytesIO()
    joblib.dump(payload or {"fake": "model"}, buf)
    storage.save(tenant_id, key, buf.getvalue())
    return key


@pytest.fixture()
def storage():
    return FakeStorage()


class TestGet:
    def test_loads_on_miss_and_caches(self, storage):
        tenant, version = uuid.uuid4(), uuid.uuid4()
        key = _seed(storage, tenant, version)
        cache = ModelCache(storage, max_size=2)

        first = cache.get(tenant, version, key)
        second = cache.get(tenant, version, key)

        assert first == {"fake": "model"}
        assert second is first  # same object: served from cache
        assert storage.reads == 1

    def test_scoped_per_tenant(self, storage):
        tenant_a, tenant_b = uuid.uuid4(), uuid.uuid4()
        version = uuid.uuid4()
        _seed(storage, tenant_a, version, payload={"tenant": "a"})
        _seed(storage, tenant_b, version, payload={"tenant": "b"})
        cache = ModelCache(storage, max_size=2)

        assert cache.get(tenant_a, version, "models/v1.joblib") == {"tenant": "a"}
        assert cache.get(tenant_b, version, "models/v1.joblib") == {"tenant": "b"}

    def test_missing_artifact_raises(self, storage):
        cache = ModelCache(storage, max_size=2)

        with pytest.raises(FileNotFoundError):
            cache.get(uuid.uuid4(), uuid.uuid4(), "models/missing.joblib")


class TestEviction:
    def test_evicts_least_recently_used(self, storage):
        tenants = [uuid.uuid4() for _ in range(3)]
        versions = [uuid.uuid4() for _ in range(3)]
        for tenant, version in zip(tenants, versions):
            _seed(storage, tenant, version)
        cache = ModelCache(storage, max_size=2)

        cache.get(tenants[0], versions[0], "models/v1.joblib")
        cache.get(tenants[1], versions[1], "models/v1.joblib")
        cache.get(tenants[0], versions[0], "models/v1.joblib")  # touch 0
        cache.get(tenants[2], versions[2], "models/v1.joblib")  # evicts 1

        # 0 is still cached (no extra read); 1 was evicted (re-read from storage).
        reads_before = storage.reads
        cache.get(tenants[0], versions[0], "models/v1.joblib")
        assert storage.reads == reads_before
        cache.get(tenants[1], versions[1], "models/v1.joblib")
        assert storage.reads == reads_before + 1


class TestInvalidation:
    def test_invalidate_forces_reload(self, storage):
        tenant, version = uuid.uuid4(), uuid.uuid4()
        key = _seed(storage, tenant, version)
        cache = ModelCache(storage, max_size=2)

        cache.get(tenant, version, key)
        cache.invalidate(tenant, version)
        cache.get(tenant, version, key)

        assert storage.reads == 2

    def test_invalidate_unknown_is_noop(self, storage):
        cache = ModelCache(storage, max_size=2)

        cache.invalidate(uuid.uuid4(), uuid.uuid4())  # no error


class TestValidation:
    def test_rejects_zero_max_size(self):
        with pytest.raises(ValueError):
            ModelCache(FakeStorage(), max_size=0)
