# Коворкинг: Бронирование переговорных

REST API сервис для бронирования переговорных комнат в коворкинге. 
Построен на FastAPI + SQLAlchemy + PostgreSQL.

## Возможности

- Аутентификация по логину/паролю с выдачей JWT-токена
- Просмотр списка переговорных комнат
- Проверка доступности слотов на конкретную дату
- Бронирование свободного слота
- Просмотр своих бронирований
- Отмена бронирования

## Стек

- **Python 3.12**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2** — ORM
- **PostgreSQL 16** — база данных
- **python-jose** — JWT-токены
- **passlib + bcrypt** — хеширование паролей
- **Docker / Docker Compose** — контейнеризация

## Структура проекта

```
app/
├── api/                # Роутеры (эндпоинты)
│   ├── auth.py
│   ├── bookings.py
│   └── rooms.py
├── core/               # Конфигурация, безопасность, зависимости
│   ├── config.py
│   ├── dependencies.py
│   ├── security.py
│   └── seed.py
├── db/                 # Модели и подключение к БД
│   ├── base.py
│   ├── models.py
│   └── session.py
├── schemas/            # Pydantic-схемы (запрос/ответ)
│   ├── booking.py
│   ├── room.py
│   └── user.py
└── services/           # Бизнес-логика
    ├── auth.py
    ├── booking.py
    └── room.py
```

## Быстрый старт

### Через Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно на **http://localhost:8000**

### Локально

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
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
uvicorn app.main:app --reload
```

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

### Примеры запросов

**Логин:**

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "admin123"}'
```

**Список комнат (с токеном):**

```bash
curl http://localhost:8000/rooms \
  -H "Authorization: Bearer <your_token>"
```

**Доступность слотов на дату:**

```bash
curl "http://localhost:8000/rooms/availability?date=2026-07-16" \
  -H "Authorization: Bearer <your_token>"
```

**Создание бронирования:**

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"slot_id": 1, "booking_date": "2026-07-16"}'
```

## Начальные данные

При первом запуске создаются:

- Пользователь **admin** / `admin123` (роль: admin)
- Пользователь **employee** / `emp123` (роль: employee)
- 2 переговорные комнаты с 3 слотами каждая

## Переменные окружения

| Переменная                    | По умолчанию                    | Описание              |
|-------------------------------|---------------------------------|-----------------------|
| `DATABASE_URL`                | —                               | URL подключения к БД  |
| `SECRET_KEY`                  | super-secret-key-change-in-prod  | Секретный ключ JWT    |
| `ALGORITHM`                   | HS256                           | Алгоритм JWT          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 60                              | Время жизни токена    |
