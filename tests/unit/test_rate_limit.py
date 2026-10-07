"""Unit tests for the in-memory rate limiter."""

import pytest

from musicrec.core.rate_limit import RateLimiter


class TestCheck:
    def test_allows_up_to_max_requests(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)

        assert limiter.check("key", now=0.0) is True
        assert limiter.check("key", now=1.0) is True
        assert limiter.check("key", now=2.0) is True

    def test_rejects_beyond_max_requests(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for i in range(3):
            limiter.check("key", now=float(i))

        assert limiter.check("key", now=3.0) is False

    def test_window_slides(self):
        limiter = RateLimiter(max_requests=2, window_seconds=10)

        assert limiter.check("key", now=0.0) is True
        assert limiter.check("key", now=1.0) is True
        assert limiter.check("key", now=5.0) is False  # 2 hits inside window
        assert limiter.check("key", now=10.5) is True  # oldest hit has expired

    def test_keys_are_independent(self):
        limiter = RateLimiter(max_requests=1, window_seconds=60)

        assert limiter.check("a", now=0.0) is True
        assert limiter.check("b", now=0.0) is True
        assert limiter.check("a", now=0.0) is False

    def test_rejected_requests_do_not_consume_budget(self):
        limiter = RateLimiter(max_requests=1, window_seconds=10)

        assert limiter.check("key", now=0.0) is True
        for i in range(5):
            assert limiter.check("key", now=1.0 + i) is False

        # The window is still governed by the single accepted hit.
        assert limiter.check("key", now=10.5) is True


class TestRetryAfter:
    def test_zero_when_under_limit(self):
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        limiter.check("key", now=0.0)

        assert limiter.retry_after("key", now=1.0) == 0.0

    def test_positive_when_exhausted(self):
        limiter = RateLimiter(max_requests=2, window_seconds=10)
        limiter.check("key", now=0.0)
        limiter.check("key", now=1.0)

        # Oldest hit expires at t=10; retry allowed from then on.
        assert limiter.retry_after("key", now=2.0) == pytest.approx(8.0)

    def test_zero_for_unknown_key(self):
        limiter = RateLimiter(max_requests=2, window_seconds=10)

        assert limiter.retry_after("nobody", now=0.0) == 0.0


class TestValidation:
    def test_rejects_zero_max_requests(self):
        with pytest.raises(ValueError):
            RateLimiter(max_requests=0, window_seconds=60)

    def test_rejects_zero_window(self):
        with pytest.raises(ValueError):
            RateLimiter(max_requests=10, window_seconds=0)
