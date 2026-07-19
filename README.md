# Коворкинг: Бронирование переговорных

REST API сервис для бронирования переговорных комнат в коворкинге.
Построен на FastAPI + SQLAlchemy + PostgreSQL.

## Возможности

- Аутентификация по логину/паролю с выдачей JWT-токена (ограниченный срок действия)
- Просмотр списка переговорных комнат
- Проверка доступности слотов на конкретную дату
- Бронирование свободного слота
- Просмотр своих бронирований (изоляция данных между пользователями)
- Отмена бронирования (своего — сотрудником, любого — админом)

## Стек

- **Python 3.13**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2** — ORM
- **PostgreSQL 16** — база данных
- **python-jose** — JWT-токены
- **passlib + bcrypt** — хеширование паролей
- **Poetry** — управление зависимостями
- **Docker / Docker Compose** — контейнеризация

## Структура проекта

```
app/
├── api/                # Роутеры (HTTP-эндпоинты)
│   ├── auth.py         #   POST /auth/login
│   ├── bookings.py     #   POST/GET/DELETE /bookings
│   └── rooms.py        #   GET /rooms, /rooms/availability
├── core/               # Конфигурация, безопасность, зависимости
│   ├── config.py       #   Настройки из .env (pydantic-settings)
│   ├── dependencies.py #   get_current_user — извлечение пользователя из JWT
│   ├── security.py     #   Хеширование паролей, создание/проверка JWT
│   └── seed.py         #   Начальные данные при первом запуске
├── db/                 # Модели и подключение к БД
│   ├── base.py         #   DeclarativeBase
│   ├── models.py       #   User, Room, Slot, Booking
│   └── session.py      #   Движок и сессия SQLAlchemy
├── schemas/            # Pydantic-схемы (запрос/ответ)
│   ├── booking.py      #   BookingCreate, BookingOut
│   ├── room.py         #   RoomOut, SlotOut, RoomWithSlotsOut
│   └── user.py         #   UserLogin, Token, UserOut
└── services/           # Бизнес-логика (изолирована от HTTP-слоя)
    ├── auth.py         #   Аутентификация пользователя
    ├── booking.py      #   Создание, просмотр, отмена броней
    └── room.py         #   Список комнат, доступность слотов
tests/
├── conftest.py         # Фикстуры: тестовая БД (SQLite), клиент, пользователи
├── test_auth.py        # Интеграционные тесты /auth/login
├── test_bookings.py    # Интеграционные тесты /bookings
├── test_rooms.py       # Интеграционные тесты /rooms
├── test_health.py      # Интеграционные тесты /health и middleware
├── test_jwt.py         # Тесты истечения JWT-токена
└── test_unit.py        # Юнит-тесты сервисного слоя (mock)
```

## Быстрый старт

### Через Docker Compose (рекомендуется)

Поднимает и API, и PostgreSQL одной командой:

```bash
docker compose up --build
```

Приложение будет доступно на **http://localhost:8000**

### Через docker run

Если PostgreSQL уже запущен отдельно:

```bash
docker build -t coworking-booking .

docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://coworking:coworking123@host.docker.internal:5432/coworking \
  -e SECRET_KEY=your-secret-key \
  coworking-booking
```

### Локально (через Poetry)

```bash
poetry install
```

Создайте файл `.env`:

```env
DATABASE_URL=postgresql://coworking:coworking123@localhost:5432/coworking
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Запустите приложение:

```bash
poetry run uvicorn app.main:app --reload
```

## Тесты

```bash
# Все тесты (юнит + интеграционные)
poetry run pytest -v

# Только интеграционные
poetry run pytest tests/test_auth.py tests/test_bookings.py tests/test_rooms.py tests/test_health.py -v

# Только юнит-тесты
poetry run pytest tests/test_unit.py -v
```

**40 тестов** покрывают:
- **Юнит-тесты (11):** сервисный слой с mock-объектами (создание брони, отмена, права, аутентификация, комнаты)
- **Интеграционные (29):** полный цикл HTTP-запросов через TestClient + SQLite
  - Аутентификация (успех, неверные данные, валидация)
  - Комнаты (список, доступность слотов, фильтрация по дате)
  - Бронирования (создание, дубликат, свои бронирования, отмена, права доступа)
  - Защита эндпоинтов (без токена, невалидный токен)
  - Истечение JWT-токена

## API

Документация доступна после запуска:

- Swagger UI — `http://localhost:8000/docs`
- ReDoc — `http://localhost:8000/redoc`

### Эндпоинты

| Метод  | Путь                     | Описание                          | Авторизация |
|--------|--------------------------|-----------------------------------|-------------|
| POST   | `/auth/login`            | Вход, получение JWT-токена        | Нет         |
| GET    | `/rooms`                 | Список переговорных               | Да          |
| GET    | `/rooms/availability`    | Доступность слотов на дату        | Да          |
| POST   | `/bookings`              | Забронировать слот                | Да          |
| GET    | `/bookings/my`           | Мои бронирования                  | Да          |
| DELETE | `/bookings/{booking_id}` | Отменить бронирование             | Да          |
| GET    | `/health`                | Проверка работоспособности        | Нет         |

### Примеры запросов и ответов

**1. Вход (получение токена):**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "admin123"}'
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**2. Список комнат:**

```bash
curl http://localhost:8000/rooms \
  -H "Authorization: Bearer <your_token>"
```

Ответ:

```json
[
  {"id": 1, "name": "Переговорка А"},
  {"id": 2, "name": "Переговорка Б"}
]
```

**3. Доступность слотов на дату:**

```bash
curl "http://localhost:8000/rooms/availability?date=2026-07-20" \
  -H "Authorization: Bearer <your_token>"
```

Ответ:

```json
[
  {
    "id": 1,
    "name": "Переговорка А",
    "slots": [
      {"id": 1, "start_time": "09:00:00", "end_time": "11:00:00", "is_booked": false},
      {"id": 2, "start_time": "11:00:00", "end_time": "13:00:00", "is_booked": false},
      {"id": 3, "start_time": "14:00:00", "end_time": "17:00:00", "is_booked": false}
    ]
  }
]
```

**4. Создание бронирования:**

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 1, "booking_date": "2026-07-20"}'
```

Ответ (201 Created):

```json
{
  "id": 1,
  "user_id": 1,
  "slot_id": 1,
  "booking_date": "2026-07-20",
  "room_name": "Переговорка А",
  "start_time": "09:00",
  "end_time": "11:00"
}
```

**5. Мои бронирования:**

```bash
curl http://localhost:8000/bookings/my \
  -H "Authorization: Bearer <your_token>"
```

Ответ:

```json
[
  {
    "id": 1,
    "user_id": 1,
    "slot_id": 1,
    "booking_date": "2026-07-20",
    "room_name": "Переговорка А",
    "start_time": "09:00",
    "end_time": "11:00"
  }
]
```

**6. Отмена бронирования (своего — сотрудником, любого — админом):**

```bash
curl -X DELETE http://localhost:8000/bookings/1 \
  -H "Authorization: Bearer <your_token>"
```

Ответ: `204 No Content` (пустое тело)

## Начальные данные

При первом запуске создаются:

- Пользователь **admin** / `admin123` (роль: admin)
- Пользователь **employee** / `emp123` (роль: employee)
- 2 переговорные комнаты с 3 слотами каждая:
  - «Переговорка А»: 09:00–11:00, 11:00–13:00, 14:00–17:00
  - «Переговорка Б»: 09:00–12:00, 13:00–16:00, 16:00–18:00

## Переменные окружения

| Переменная                    | По умолчанию                     | Описание              |
|-------------------------------|----------------------------------|-----------------------|
| `DATABASE_URL`                | postgresql://coworking:...       | URL подключения к БД  |
| `SECRET_KEY`                  | super-secret-key-change-in-prod  | Секретный ключ JWT    |
| `ALGORITHM`                   | HS256                            | Алгоритм JWT          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60                               | Время жизни токена    |

## Архитектура

Сервис следует трёхуровневой архитектуре:

```
API (роутеры) → Services (бизнес-логика) → DB (ORM-модели)
```

- **API-слой** (`app/api/`) — принимает HTTP-запросы, валидирует через Pydantic-схемы, вызывает сервисы
- **Сервисный слой** (`app/services/`) — содержит бизнес-логику, не зависит от HTTP
- **Слой данных** (`app/db/`) — SQLAlchemy-модели и сессия БД

Такое разделение позволяет тестировать бизнес-логику изолированно (юнит-тесты с mock) и независимо менять реализацию каждого слоя.
