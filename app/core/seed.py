from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import User, Room, Slot, UserRole
from app.core.security import hash_password


def seed_initial_data() -> None:
    """
    Создаёт начальные данные при первом запуске.
    Безопасно вызывать повторно — проверяет наличие записей.
    """
    db: Session = SessionLocal()
    try:
        _seed_users(db)
        _seed_rooms_and_slots(db)
    finally:
        db.close()


def _seed_users(db: Session) -> None:
    if db.query(User).filter(User.login == "admin").first() is None:
        db.add(User(
            login="admin",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
        ))
    if db.query(User).filter(User.login == "employee").first() is None:
        db.add(User(
            login="employee",
            hashed_password=hash_password("emp123"),
            role=UserRole.EMPLOYEE,
        ))
    db.commit()


def _seed_rooms_and_slots(db: Session) -> None:
    """Создаёт 2 комнаты и для каждой — 3 временных слота."""
    if db.query(Room).count() > 0:
        return  # уже заполнено

    rooms_data = [
        {"name": "Переговорка А", "slots": [("09:00", "11:00"), ("11:00", "13:00"), ("14:00", "17:00")]},
        {"name": "Переговорка Б", "slots": [("09:00", "12:00"), ("13:00", "16:00"), ("16:00", "18:00")]},
    ]

    from datetime import time as dtime

    for room_data in rooms_data:
        room = Room(name=room_data["name"])
        db.add(room)
        db.flush()  # чтобы получить room.id

        for start_str, end_str in room_data["slots"]:
            start_h, start_m = map(int, start_str.split(":"))
            end_h, end_m = map(int, end_str.split(":"))
            db.add(Slot(
                room_id=room.id,
                start_time=dtime(start_h, start_m),
                end_time=dtime(end_h, end_m),
            ))

    db.commit()