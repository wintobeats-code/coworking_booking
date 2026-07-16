"""Тесты системных эндпоинтов."""


class TestHealthCheck:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthMiddleware:
    def test_protected_endpoint_without_token(self, client):
        response = client.get("/rooms")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client):
        response = client.get(
            "/rooms",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_bearer_prefix(self, client, employee_token):
        response = client.get(
            "/rooms",
            headers={"Authorization": employee_token},
        )
        assert response.status_code == 401
