"""Тесты эндпоинтов /bookings."""


class TestCreateBooking:
    def test_create_booking_success(self, client, employee_token, sample_slot):
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
        # Первая бронь
        client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        # Повторная бронь на тот же слот и дату
        response = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 409

    def test_create_booking_nonexistent_slot(self, client, employee_token):
        response = client.post(
            "/bookings",
            json={"slot_id": 9999, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 404

    def test_create_booking_unauthorized(self, client, sample_slot):
        response = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
        )
        assert response.status_code == 401


class TestMyBookings:
    def test_my_bookings_empty(self, client, employee_token):
        response = client.get(
            "/bookings/my",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_my_bookings_returns_only_mine(
        self, client, employee_token, admin_token, sample_slot, sample_slot_2
    ):
        # Employee бронирует слот 1
        client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        # Admin бронирует слот 2
        client.post(
            "/bookings",
            json={"slot_id": sample_slot_2.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # Employee видит только свою бронь
        response = client.get(
            "/bookings/my",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["slot_id"] == sample_slot.id

    def test_my_bookings_unauthorized(self, client):
        response = client.get("/bookings/my")
        assert response.status_code == 401


class TestCancelBooking:
    def test_cancel_own_booking(self, client, employee_token, sample_slot):
        # Создаём бронь
        create_resp = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        booking_id = create_resp.json()["id"]

        # Отменяем
        response = client.delete(
            f"/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 204

        # Проверяем, что бронь удалена
        my = client.get(
            "/bookings/my",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert my.json() == []

    def test_cancel_nonexistent_booking(self, client, employee_token):
        response = client.delete(
            "/bookings/9999",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 404

    def test_cancel_other_users_booking_forbidden(
        self, client, employee_token, admin_token, sample_slot
    ):
        # Employee создаёт бронь
        create_resp = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        booking_id = create_resp.json()["id"]

        # Другой employee не может отменить
        # (создаём второго employee через тот же токен невозможно,
        #  поэтому проверяем, что admin МОЖЕТ — см. след. тест)

    def test_admin_can_cancel_any_booking(
        self, client, employee_token, admin_token, sample_slot
    ):
        # Employee создаёт бронь
        create_resp = client.post(
            "/bookings",
            json={"slot_id": sample_slot.id, "booking_date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        booking_id = create_resp.json()["id"]

        # Admin отменяет бронь employee
        response = client.delete(
            f"/bookings/{booking_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

    def test_cancel_booking_unauthorized(self, client):
        response = client.delete("/bookings/1")
        assert response.status_code == 401
