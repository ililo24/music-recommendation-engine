"""In-memory, per-key rate limiting (config-driven).

Framework-agnostic: the limiter knows nothing about FastAPI or HTTP — the
dependency in ``api/deps.py`` feeds it the caller's identity (API-key id, or
user id for JWT callers). State is per-process: with multiple server workers
each process enforces the limit independently. A Redis-backed limiter can
replace this without changing callers if cross-process limits are needed.

Only accepted requests consume budget (token-bucket semantics): a rejected
request does not extend the caller's window.
"""

import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    """Sliding-window rate limiter keyed by an arbitrary hashable key."""

    def __init__(self, max_requests: int, window_seconds: float) -> None:
        """Create a limiter allowing ``max_requests`` per ``window_seconds``."""
        if max_requests < 1:
            raise ValueError("max_requests must be >= 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, *, now: float | None = None) -> bool:
        """Record a hit for ``key`` and return whether it is within budget.

        ``now`` (monotonic seconds) is injectable for tests.
        """
        moment = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits[key]
            cutoff = moment - self._window_seconds
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self._max_requests:
                return False
            hits.append(moment)
            return True

    def retry_after(self, key: str, *, now: float | None = None) -> float:
        """Seconds until ``key`` may make its next accepted request (0 if now).

        Used for the ``Retry-After`` header on 429 responses.
        """
        moment = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits.get(key)
            if not hits or len(hits) < self._max_requests:
                return 0.0
            return max(0.0, hits[0] + self._window_seconds - moment)
