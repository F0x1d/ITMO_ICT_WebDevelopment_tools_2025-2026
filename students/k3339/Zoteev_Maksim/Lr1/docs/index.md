# Лабораторная работа 1

## Тема

Разработка веб-приложения для поиска партнеров в путешествие.

Приложение позволяет:

- регистрировать пользователей и авторизовывать их через JWT
- создавать поездки и управлять ими
- добавлять остановки в маршрут
- искать и просматривать пользователей и поездки
- связывать пользователей с интересами
- добавлять участников в поездки

## Ссылки на GitHub

- Репозиторий: [ITMO_ICT_WebDevelopment_tools_2025-2026](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026)
- Практика 1.1: [task1](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3339/Zoteev_Maksim/Lr1/task1)
- Практика 1.2: [task2](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3339/Zoteev_Maksim/Lr1/task2)
- Практика 1.3: [task3](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3339/Zoteev_Maksim/Lr1/task3)
- Лабораторная работа: [lab](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/main/students/k3339/Zoteev_Maksim/Lr1/lab)

## Используемые технологии

- FastAPI
- SQLModel
- PostgreSQL
- Alembic
- PyJWT
- Passlib bcrypt
- Docker Compose

## Подключение к БД

Файл: [`lab/app/core/config.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/core/config.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:123@localhost/travel_partner_lab"
    jwt_secret_key: str = "super-secret-jwt-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
```

Файл: [`lab/app/db/session.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/db/session.py)

```python
from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(settings.database_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
```

## Модели данных

Всего используется 6 таблиц.

### 1. `users`

Файл: [`lab/app/models/user.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/models/user.py)

Поля:

- `id`
- `email`
- `username`
- `full_name`
- `age`
- `city`
- `bio`
- `travel_style`
- `telegram_username`
- `languages`
- `password_hash`

### 2. `interests`

Файл: [`lab/app/models/interest.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/models/interest.py)

Поля:

- `id`
- `name`
- `description`

### 3. `trips`

Файл: [`lab/app/models/trip.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/models/trip.py)

Поля:

- `id`
- `title`
- `departure_city`
- `destination_city`
- `start_date`
- `end_date`
- `duration_days`
- `description`
- `organizer_id`

### 4. `trip_stops`

Файл: [`lab/app/models/trip.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/models/trip.py)

Поля:

- `id`
- `trip_id`
- `location`
- `days`
- `note`

### 5. `user_interests`

Ассоциативная сущность many-to-many между пользователями и интересами.

Файл: [`lab/app/models/interest.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/models/interest.py)

Поля:

- `user_id`
- `interest_id`
- `experience_level`

### 6. `trip_participants`

Ассоциативная сущность many-to-many между пользователями и поездками.

Файл: [`lab/app/models/trip.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/models/trip.py)

Поля:

- `id`
- `trip_id`
- `user_id`
- `status`
- `message`
- `contact_preference`

## Связи между таблицами

- `users -> trips` : one-to-many
- `trips -> trip_stops` : one-to-many
- `users <-> interests` : many-to-many через `user_interests`
- `users <-> trips` : many-to-many через `trip_participants`

Ассоциативные сущности содержат собственные поля, характеризующие связь:

- `user_interests.experience_level`
- `trip_participants.status`
- `trip_participants.message`
- `trip_participants.contact_preference`

## JWT, авторизация и безопасность

Файлы:

- [`lab/app/core/security.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/core/security.py)
- [`lab/app/api/deps.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/api/deps.py)
- [`lab/app/services/auth.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/services/auth.py)

Реализовано:

- регистрация пользователя
- логин пользователя
- генерация JWT токена
- проверка токена в защищенных эндпоинтах
- хэширование пароля через bcrypt
- смена пароля

## Миграции Alembic

Файлы:

- [`lab/alembic.ini`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/alembic.ini)
- [`lab/migrations/env.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/migrations/env.py)
- [`lab/migrations/versions/0001_initial_schema.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/migrations/versions/0001_initial_schema.py)
- [`lab/migrations/versions/0002_add_telegram_and_contact_preference.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/migrations/versions/0002_add_telegram_and_contact_preference.py)

В проекте есть две миграции:

1. создание начальной схемы БД
2. добавление полей `telegram_username` и `contact_preference`

## Все реализованные эндпоинты

### Сервисные

- `GET /` - проверка доступности API

### Auth

Файл: [`lab/app/api/routes/auth.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/api/routes/auth.py)

- `POST /auth/register` - регистрация пользователя
- `POST /auth/login` - логин и получение JWT токена

### Users

Файл: [`lab/app/api/routes/users.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/api/routes/users.py)

- `GET /users` - список пользователей
- `GET /users/me` - информация о текущем пользователе
- `GET /users/{user_id}` - информация о пользователе по id
- `PATCH /users/me` - изменение профиля текущего пользователя
- `POST /users/me/change-password` - смена пароля
- `DELETE /users/me` - удаление текущего пользователя
- `POST /users/me/interests` - добавить интерес текущему пользователю
- `PATCH /users/me/interests/{interest_id}` - изменить уровень опыта по интересу
- `DELETE /users/me/interests/{interest_id}` - удалить интерес у текущего пользователя

### Interests

Файл: [`lab/app/api/routes/interests.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/api/routes/interests.py)

- `GET /interests` - список интересов
- `GET /interests/{interest_id}` - интерес по id
- `POST /interests` - создание интереса
- `PATCH /interests/{interest_id}` - изменение интереса
- `DELETE /interests/{interest_id}` - удаление интереса

### Trips

Файл: [`lab/app/api/routes/trips.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/api/routes/trips.py)

- `GET /trips` - список поездок
- `GET /trips/{trip_id}` - поездка по id с вложенными объектами
- `POST /trips` - создание поездки
- `PATCH /trips/{trip_id}` - изменение поездки
- `DELETE /trips/{trip_id}` - удаление поездки
- `POST /trips/{trip_id}/stops` - добавить остановку в поездку
- `PATCH /trips/stops/{stop_id}` - изменить остановку
- `DELETE /trips/stops/{stop_id}` - удалить остановку
- `POST /trips/{trip_id}/participants` - добавить участника в поездку
- `PATCH /trips/participants/{participant_id}` - изменить участие в поездке
- `DELETE /trips/participants/{participant_id}` - удалить участника из поездки

## Вложенные модели в GET-запросах

В соответствии с требованиями лабораторной реализованы вложенные ответы для связанных сущностей.

### `GET /users/{user_id}` и `GET /users/me`

Возвращают:

- данные пользователя
- список интересов с объектами `interest`
- список созданных поездок
- список поездок, в которых пользователь участвует

### `GET /trips/{trip_id}`

Возвращает:

- данные поездки
- вложенный объект организатора
- список остановок
- список участников с вложенными объектами пользователей

## Примеры ключевых файлов

### Главный роутер

Файл: [`lab/app/api/router.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/api/router.py)

```python
from fastapi import APIRouter

from app.api.routes import auth, interests, trips, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(interests.router)
api_router.include_router(trips.router)
```

### Подключение роутера в FastAPI

Файл: [`lab/app/main.py`](https://github.com/F0x1d/ITMO_ICT_WebDevelopment_tools_2025-2026/blob/main/students/k3339/Zoteev_Maksim/Lr1/lab/app/main.py)

```python
from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Travel Partner Finder API")
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Travel Partner Finder API"}
```

## Запуск проекта

### Через Docker Compose

```bash
cd lab
docker compose up -d
pip install -r requirements.txt
alembic upgrade head
python seed.py
uvicorn app.main:app --reload
```

### Swagger UI

После запуска документация доступна по адресу:

```text
http://127.0.0.1:8000/docs
```

## Вывод

В рамках лабораторной работы было разработано серверное приложение на FastAPI для поиска попутчиков. В проекте реализованы:

- полноценная структура FastAPI-проекта
- PostgreSQL и ORM SQLModel
- миграции Alembic
- CRUD API
- вложенные ответы для связанных моделей
- авторизация и регистрация
- JWT-аутентификация
- хэширование паролей
- дополнительные методы для работы с текущим пользователем

Таким образом, работа покрывает требования на 15 баллов.
