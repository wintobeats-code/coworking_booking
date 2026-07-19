"""Тесты эндпоинтов /rooms."""

from datetime import date

from app.db.models import Booking


class TestListRooms:
    """Проверки GET /rooms."""

    def test_list_rooms_empty(self, client, employee_token):
        """Пустой список при отсутствии комнат."""
        response = client.get(
            "/rooms", headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_list_rooms_returns_rooms(  # pylint: disable=unused-argument
        self, client, employee_token, sample_room, second_room
    ):
        """Возвращает все созданные комнаты."""
        response = client.get(
            "/rooms", headers={"Authorization": f"Bearer {employee_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = {r["name"] for r in data}
        assert names == {"Переговорка А", "Переговорка Б"}

    def test_list_rooms_unauthorized(self, client):
        """Без токена возвращает 401."""
        response = client.get("/rooms")
        assert response.status_code == 401


class TestRoomsAvailability:
    """Проверки GET /rooms/availability."""

    def test_availability_with_slots(  # pylint: disable=unused-argument
        self, client, employee_token, sample_room, sample_slot, sample_slot_2
    ):
        """Свободные слоты отображаются корректно."""
        response = client.get(
            "/rooms/availability",
            params={"date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        room = data[0]
        assert room["name"] == "Переговорка А"
        assert len(room["slots"]) == 2
        assert all(s["is_booked"] is False for s in room["slots"])

    def test_availability_slot_booked(  # pylint: disable=unused-argument
        self,
        client,
        employee_token,
        user_employee,
        sample_room,
        sample_slot,
        sample_slot_2,
        db_session,
    ):
        """Забронированный слот помечается is_booked=True."""
        db_session.add(
            Booking(
                user_id=user_employee.id,
                slot_id=sample_slot.id,
                booking_date=date(2026, 7, 20),
            )
        )
        db_session.commit()

        response = client.get(
            "/rooms/availability",
            params={"date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        slots = data[0]["slots"]
        booked = [s for s in slots if s["is_booked"]]
        free = [s for s in slots if not s["is_booked"]]
        assert len(booked) == 1
        assert len(free) == 1

    def test_availability_no_bookings_on_date(  # pylint: disable=unused-argument
        self,
        client,
        employee_token,
        user_employee,
        sample_room,
        sample_slot,
        db_session,
    ):
        """Бронь на другой день не влияет на доступность."""
        db_session.add(
            Booking(
                user_id=user_employee.id,
                slot_id=sample_slot.id,
                booking_date=date(2026, 7, 21),
            )
        )
        db_session.commit()

        response = client.get(
            "/rooms/availability",
            params={"date": "2026-07-20"},
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 200
        slots = response.json()[0]["slots"]
        assert all(s["is_booked"] is False for s in slots)

    def test_availability_unauthorized(self, client):
        """Без токена доступность возвращает 401."""
        response = client.get("/rooms/availability", params={"date": "2026-07-20"})
        assert response.status_code == 401

    def test_availability_missing_date_param(self, client, employee_token):
        """Без параметра date возвращает 422."""
        response = client.get(
            "/rooms/availability",
            headers={"Authorization": f"Bearer {employee_token}"},
        )
        assert response.status_code == 422
