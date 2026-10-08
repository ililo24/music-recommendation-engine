"""Integration tests for the API skeleton (TestClient, no auth/DB yet)."""

import pytest
from fastapi.testclient import TestClient

from musicrec.main import create_app


@pytest.fixture()
def client() -> TestClient:
    """TestClient against a freshly created app."""
    return TestClient(create_app())


@pytest.fixture()
def client_with_test_routes() -> TestClient:
    """TestClient against an app with temporary routes used to trigger the
    validation and unhandled-exception handlers.

    ``raise_server_exceptions=False`` is required for the 500 test: Starlette's
    ServerErrorMiddleware sends the handler's response and then re-raises, and
    the default TestClient would propagate that instead of returning it.
    """
    app = create_app()

    @app.get("/api/v1/_test/validated")
    async def validated_endpoint(number: int):
        return {"number": number}

    @app.get("/api/v1/_test/boom")
    async def boom_endpoint():
        raise RuntimeError("boom")

    return TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    """GET /api/v1/health"""

    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_response_schema(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")

        body = response.json()
        assert set(body) == {"status", "version", "environment", "timestamp"}
        assert body["version"]
        assert body["environment"]

    def test_health_returns_json(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")

        assert response.headers["content-type"].startswith("application/json")


class TestErrorSchema:
    """Every error response uses the consistent error envelope."""

    def test_unknown_route_returns_error_schema(self, client: TestClient) -> None:
        response = client.get("/api/v1/does-not-exist")

        assert response.status_code == 404
        body = response.json()
        assert set(body) == {"error", "request_id"}
        assert body["error"]["code"] == "not_found"
        assert body["error"]["message"]

    def test_request_validation_error_returns_error_schema(
        self, client_with_test_routes: TestClient
    ) -> None:
        response = client_with_test_routes.get("/api/v1/_test/validated")

        assert response.status_code == 422
        body = response.json()
        assert body["error"]["code"] == "validation_error"
        assert "errors" in body["error"]["details"]

    def test_unhandled_exception_returns_error_schema(
        self, client_with_test_routes: TestClient
    ) -> None:
        response = client_with_test_routes.get("/api/v1/_test/boom")

        assert response.status_code == 500
        body = response.json()
        assert body["error"]["code"] == "internal_error"
        assert body["error"]["message"] == "Internal server error"


class TestRequestIds:
    """Request id propagation (response header + error bodies)."""

    def test_response_carries_request_id_header(self, client: TestClient) -> None:
        response = client.get("/api/v1/health")

        assert response.headers["x-request-id"]

    def test_incoming_request_id_is_reused(self, client: TestClient) -> None:
        response = client.get("/api/v1/health", headers={"X-Request-ID": "test-req-123"})

        assert response.headers["x-request-id"] == "test-req-123"

    def test_error_body_reuses_incoming_request_id(self, client: TestClient) -> None:
        response = client.get(
            "/api/v1/does-not-exist", headers={"X-Request-ID": "test-req-456"}
        )

        assert response.json()["request_id"] == "test-req-456"


class TestCORS:
    """CORS middleware driven by config (defaults allow all origins)."""

    def test_simple_request_gets_cors_headers(self, client: TestClient) -> None:
        response = client.get(
            "/api/v1/health", headers={"Origin": "http://localhost:3000"}
        )

        assert response.headers.get("access-control-allow-origin") == "*"

    def test_preflight_request(self, client: TestClient) -> None:
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "*"
