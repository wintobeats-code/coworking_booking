"""Тесты системных эндпоинтов (health, middleware)."""


class TestHealthCheck:
    """Проверки /health."""

    def test_health(self, client):
        """Эндпоинт здоровья возвращает status=ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthMiddleware:
    """Проверки защиты эндпоинтов токеном."""

    def test_protected_endpoint_without_token(self, client):
        """Запрос без токена возвращает 401."""
        response = client.get("/rooms")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self, client):
        """Невалидный токен возвращает 401."""
        response = client.get(
            "/rooms",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_protected_endpoint_without_bearer_prefix(self, client, employee_token):
        """Токен без префикса Bearer возвращает 401."""
        response = client.get(
            "/rooms",
            headers={"Authorization": employee_token},
        )
        assert response.status_code == 401
