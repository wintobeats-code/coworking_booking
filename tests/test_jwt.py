"""Тесты JWT-токена: декодирование, истечение срока, невалидный формат."""

from datetime import datetime, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.security import create_access_token, decode_access_token
from tests.conftest import TEST_APP


class TestJWTToken:
    """Проверки срока действия и валидности JWT-токена."""

    def test_token_contains_valid_login(self):
        """Токен декодируется и содержит корректный login."""
        token = create_access_token("employee")
        login = decode_access_token(token)
        assert login == "employee"

    def test_expired_token_is_rejected(self):
        """Истёкший токен отклоняется middleware (401)."""
        with patch("app.core.security.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2020, 1, 1, tzinfo=timezone.utc)
            expired_token = create_access_token("employee")

        client = TestClient(TEST_APP, raise_server_exceptions=True)
        response = client.get(
            "/rooms",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401

    def test_invalid_token_format(self):
        """Токен с невалидным форматом возвращает None при декодировании."""
        result = decode_access_token("not.a.valid.token")
        assert result is None
