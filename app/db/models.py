"""ORM-модели базы данных."""

import enum
from datetime import date, time

from sqlalchemy import Date, ForeignKey, Integer, String, Time, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    """Роли пользователей."""

    EMPLOYEE = "employee"
    ADMIN = "admin"


class User(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        SAEnum(UserRole, name="user_role", create_constraint=True),
        default=UserRole.EMPLOYEE,
        nullable=False,
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Room(Base):
    """Модель переговорной комнаты."""

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    slots: Mapped[list["Slot"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )


class Slot(Base):
    """Модель временного слота в переговорной комнате."""

    __tablename__ = "slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    room: Mapped["Room"] = relationship(back_populates="slots")
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )


class Booking(Base):
    """Модель бронирования слота."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey("slots.id"), nullable=False)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (UniqueConstraint("slot_id", "booking_date", name="uq_slot_date"),)

    user: Mapped["User"] = relationship(back_populates="bookings")
    slot: Mapped["Slot"] = relationship(back_populates="bookings")
