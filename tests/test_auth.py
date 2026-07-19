"""Тесты эндпоинта /auth/login."""


class TestLogin:
    """Проверки входа в систему."""

    def test_login_success(self, client, user_employee):  # pylint: disable=unused-argument
        """Успешный вход с корректными данными."""
        response = client.post(
            "/auth/login",
            json={"login": "employee", "password": "emp123"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    def test_login_wrong_password(self, client, user_employee):  # pylint: disable=unused-argument
        """Вход с неверным паролем возвращает 401."""
        response = client.post(
            "/auth/login",
            json={"login": "employee", "password": "wrong"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Вход с несуществующим логином возвращает 401."""
        response = client.post(
            "/auth/login",
            json={"login": "nobody", "password": "pass"},
        )
        assert response.status_code == 401

    def test_login_short_login_validation(self, client):
        """Слишком короткий логин вызывает 422."""
        response = client.post(
            "/auth/login",
            json={"login": "ab", "password": "pass"},
        )
        assert response.status_code == 422

    def test_login_short_password_validation(self, client):
        """Слишком короткий пароль вызывает 422."""
        response = client.post(
            "/auth/login",
            json={"login": "user", "password": "abc"},
        )
        assert response.status_code == 422
