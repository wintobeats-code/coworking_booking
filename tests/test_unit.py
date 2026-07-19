"""Юнит-тесты сервисного слоя (изолированные от БД и HTTP)."""

from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.models import Booking, Room, Slot, User, UserRole
from app.services import auth as auth_svc
from app.services import booking as booking_svc
from app.services import room as room_svc


class TestBookingServiceCreate:
    """Юнит-тесты booking_svc.create_booking."""

    def test_create_booking_success(self):
        """Успешное создание бронирования — вызываются add и commit."""
        db = MagicMock()
        slot = Slot(id=1, room_id=1, start_time=MagicMock(), end_time=MagicMock())
        db.query.return_value.filter.return_value.first.return_value = slot
        db.add.return_value = None
        db.commit.return_value = None

        def mock_refresh(obj):
            obj.id = 1

        db.refresh = mock_refresh

        user = User(id=10, login="emp", role=UserRole.EMPLOYEE)

        with pytest.MonkeyPatch.context() as m:
            mock_booking = MagicMock()
            m.setattr("app.services.booking.Booking", lambda **kw: mock_booking)
            booking_svc.create_booking(
                db, slot_id=1, booking_date=date(2026, 7, 20), user=user
            )
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_create_booking_slot_not_found(self):
        """Слот не найден — выбрасывается 404."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        user = User(id=10, login="emp", role=UserRole.EMPLOYEE)

        with pytest.raises(HTTPException) as exc_info:
            booking_svc.create_booking(
                db, slot_id=999, booking_date=date(2026, 7, 20), user=user
            )
        assert exc_info.value.status_code == 404

    def test_create_booking_duplicate_slot(self):
        """Повторное бронирование слота — выбрасывается 409."""
        db = MagicMock()
        slot = Slot(id=1, room_id=1, start_time=MagicMock(), end_time=MagicMock())
        db.query.return_value.filter.return_value.first.return_value = slot
        db.commit.side_effect = IntegrityError("", "", "")
        db.rollback.return_value = None

        user = User(id=10, login="emp", role=UserRole.EMPLOYEE)

        with pytest.raises(HTTPException) as exc_info:
            booking_svc.create_booking(
                db, slot_id=1, booking_date=date(2026, 7, 20), user=user
            )
        assert exc_info.value.status_code == 409
        db.rollback.assert_called_once()


class TestBookingServiceCancel:
    """Юнит-тесты booking_svc.cancel_booking."""

    def test_cancel_own_booking(self):
        """Сотрудник может отменить свою бронь."""
        db = MagicMock()
        booking = Booking(id=1, user_id=10, slot_id=1, booking_date=date(2026, 7, 20))
        db.query.return_value.filter.return_value.first.return_value = booking
        db.delete.return_value = None
        db.commit.return_value = None

        user = User(id=10, login="emp", role=UserRole.EMPLOYEE)
        booking_svc.cancel_booking(db, booking_id=1, current_user=user)
        db.delete.assert_called_once_with(booking)
        db.commit.assert_called_once()

    def test_cancel_other_users_booking_forbidden(self):
        """Сотрудник НЕ может отменить чужую бронь — 403."""
        db = MagicMock()
        booking = Booking(id=1, user_id=10, slot_id=1, booking_date=date(2026, 7, 20))
        db.query.return_value.filter.return_value.first.return_value = booking

        other_user = User(id=20, login="other", role=UserRole.EMPLOYEE)

        with pytest.raises(HTTPException) as exc_info:
            booking_svc.cancel_booking(db, booking_id=1, current_user=other_user)
        assert exc_info.value.status_code == 403

    def test_admin_can_cancel_any_booking(self):
        """Админ может отменить любую бронь."""
        db = MagicMock()
        booking = Booking(id=1, user_id=10, slot_id=1, booking_date=date(2026, 7, 20))
        db.query.return_value.filter.return_value.first.return_value = booking
        db.delete.return_value = None
        db.commit.return_value = None

        admin = User(id=99, login="admin", role=UserRole.ADMIN)
        booking_svc.cancel_booking(db, booking_id=1, current_user=admin)
        db.delete.assert_called_once_with(booking)
        db.commit.assert_called_once()

    def test_cancel_nonexistent_booking(self):
        """Отмена несуществующей брони — 404."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        user = User(id=10, login="emp", role=UserRole.EMPLOYEE)

        with pytest.raises(HTTPException) as exc_info:
            booking_svc.cancel_booking(db, booking_id=999, current_user=user)
        assert exc_info.value.status_code == 404


class TestBookingServiceGetMy:
    """Юнит-тесты booking_svc.get_my_bookings."""

    def test_get_my_bookings_empty(self):
        """Пустой список, если бронирований нет."""
        db = MagicMock()
        db.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = []

        user = User(id=10, login="emp", role=UserRole.EMPLOYEE)
        result = booking_svc.get_my_bookings(db, user)
        assert result == []

    def test_get_my_bookings_returns_only_own(self):
        """Возвращает только бронирования указанного пользователя."""
        db = MagicMock()
        mock_room = MagicMock()
        mock_room.name = "Переговорка А"
        mock_slot = MagicMock()
        mock_slot.room = mock_room
        mock_slot.start_time = MagicMock()
        mock_slot.start_time.strftime.return_value = "09:00"
        mock_slot.end_time = MagicMock()
        mock_slot.end_time.strftime.return_value = "11:00"

        mock_booking = MagicMock()
        mock_booking.id = 1
        mock_booking.user_id = 10
        mock_booking.slot_id = 1
        mock_booking.booking_date = date(2026, 7, 20)
        mock_booking.slot = mock_slot

        db.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = [
            mock_booking
        ]

        user = User(id=10, login="emp", role=UserRole.EMPLOYEE)
        result = booking_svc.get_my_bookings(db, user)
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["room_name"] == "Переговорка А"


class TestRoomService:
    """Юнит-тесты room_svc."""

    def test_get_all_rooms(self):
        """get_all_rooms возвращает список комнат из БД."""
        db = MagicMock()
        room1 = Room(id=1, name="А")
        room2 = Room(id=2, name="Б")
        db.query.return_value.all.return_value = [room1, room2]

        result = room_svc.get_all_rooms(db)
        assert len(result) == 2

    def test_get_rooms_availability(self):
        """get_rooms_availability формирует корректную структуру."""
        db = MagicMock()

        mock_booked = MagicMock()
        mock_booked.slot_id = 1
        db.query.return_value.filter.return_value.all.return_value = [mock_booked]

        mock_slot = MagicMock()
        mock_slot.id = 1
        mock_slot.start_time = "09:00"
        mock_slot.end_time = "11:00"

        mock_room = MagicMock()
        mock_room.id = 1
        mock_room.name = "Переговорка А"
        mock_room.slots = [mock_slot]

        db.query.return_value.options.return_value.all.return_value = [mock_room]

        result = room_svc.get_rooms_availability(db, date(2026, 7, 20))
        assert len(result) == 1
        assert result[0]["name"] == "Переговорка А"
        assert len(result[0]["slots"]) == 1
        assert result[0]["slots"][0]["is_booked"] is True


class TestAuthService:
    """Юнит-тесты auth_svc.authenticate_user."""

    def test_authenticate_success(self):
        """Успешная аутентификация возвращает JWT-токен."""
        db = MagicMock()
        user = User(
            id=1,
            login="employee",
            hashed_password=hash_password("emp123"),
            role=UserRole.EMPLOYEE,
        )
        db.query.return_value.filter.return_value.first.return_value = user

        token = auth_svc.authenticate_user(db, "employee", "emp123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_authenticate_wrong_password(self):
        """Неверный пароль — 401."""
        db = MagicMock()
        user = User(
            id=1,
            login="employee",
            hashed_password=hash_password("emp123"),
            role=UserRole.EMPLOYEE,
        )
        db.query.return_value.filter.return_value.first.return_value = user

        with pytest.raises(HTTPException) as exc_info:
            auth_svc.authenticate_user(db, "employee", "wrong")
        assert exc_info.value.status_code == 401

    def test_authenticate_nonexistent_user(self):
        """Несуществующий пользователь — 401."""
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            auth_svc.authenticate_user(db, "nobody", "pass")
        assert exc_info.value.status_code == 401
