"""Тесты эндпоинтов /bookings."""


class TestCreateBooking:
    """Проверки POST /bookings."""

    def test_create_booking_success(self, client, employee_token, sample_slot):
        """Успешное создание бронирования."""
        response = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["slot_id"] == sample_slot.id
        assert data["booking_date"] == "2026-07-20"
        assert data["room_name"] == "Переговорка А"
        assert "start_time" in data
        assert "end_time" in data

    def test_create_booking_duplicate_slot(self, client, employee_token, sample_slot):
        """Повторное бронирование того же слота возвращает 409."""
        client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        response = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 409

    def test_create_booking_nonexistent_slot(self, client, employee_token):
        """Бронирование несуществующего слота возвращает 404."""
        response = client.post(
            "/bookings",
            json={"slot_id": 9999, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 404

    def test_create_booking_unauthorized(self, client, sample_slot):  # pylint: disable=unused-argument
        """Без токена создание брони возвращает 401."""
        response = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
        )
        assert response.status_code == 401


class TestMyBookings:
    """Проверки GET /bookings/my."""

    def test_my_bookings_empty(self, client, employee_token):
        """Пустой список при отсутствии бронирований."""
        response = client.get(
            "/bookings/my",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_my_bookings_returns_only_mine(  # pylint: disable=unused-argument
        self, client, employee_token, admin_token, sample_slot, sample_slot_2
    ):
        """Возвращает только бронирования текущего пользователя."""
        client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        client.post(
            "/bookings",
            json={"slot_id": sample_slot_2.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        response = client.get(
            "/bookings/my",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slot_id"] == sample_slot.id

    def test_my_bookings_unauthorized(self, client):
        """Без токена мои бронирования возвращают 401."""
        response = client.get("/bookings/my")
        assert response.status_code == 401


class TestCancelBooking:
    """Проверки DELETE /bookings/{booking_id}."""

    def test_cancel_own_booking(self, client, employee_token, sample_slot):
        """Сотрудник отменяет свою бронь — 204."""
        create_resp = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        booking_id = create_resp.json()["id"]

        response = client.delete(
            f"/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 204

        my = client.get(
            "/bookings/my",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert my.json() == []

    def test_cancel_nonexistent_booking(self, client, employee_token):
        """Отмена несуществующей брони возвращает 404."""
        response = client.delete(
            "/bookings/9999",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 404

    def test_cancel_other_users_booking_forbidden(
        self, client, employee_token, employee_2_token, sample_slot
    ):
        """Сотрудник не может отменить чужую бронь — 403."""
        create_resp = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        booking_id = create_resp.json()["id"]

        response = client.delete(
            f"/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {employee_2_token}"},
        )
        assert response.status_code == 403

    def test_admin_can_cancel_any_booking(
        self, client, employee_token, admin_token, sample_slot
    ):
        """Админ может отменить любую бронь — 204."""
        create_resp = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        booking_id = create_resp.json()["id"]

        response = client.delete(
            f"/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

    def test_cancel_booking_unauthorized(self, client):
        """Без токена отмена возвращает 401."""
        response = client.delete("/bookings/1")
        assert response.status_code == 401
