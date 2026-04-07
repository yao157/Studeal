# Studeal

Проект для управління завданнями через Telegram ботів.

## Структура проекту

- `src/database/models/` - SQLAlchemy моделі (User, Post)
- `src/database/repo/` - Репозиторії для роботи з БД (UserRepo, PostRepo)
- `config/` - Конфігурація проекту
- `migrations/` - Alembic міграції бази даних

## Налаштування

1. Встановіть залежності:
```bash
pip install -r requirements.txt
```

2. Створіть файл `.env` (орієнтир — `.env.example`): `DB__*`, `BOT__*`, інші поля з `config/config.py`.

## Запуск через Docker Compose

Піднімає **PostgreSQL** і **Task Bot**. Перед першим запуском скопіюй `.env.example` → `.env` і вкажи токени ботів та інші секрети.

```bash
docker compose up -d --build
```

У контейнері бота **автоматично** виконується `alembic upgrade head`, потім `python main.py`. Змінна `DB__HOST` для бота встановлюється на сервіс `postgres`; у `.env` для локального запуску без Docker лишай `DB__HOST=localhost`.

## Міграції бази даних (Alembic)

### Створення початкової міграції:
```bash
alembic revision --autogenerate -m "Initial migration: users and posts"
```

### Застосування міграцій:
```bash
alembic upgrade head
```

### Відкат міграції:
```bash
alembic downgrade -1
```

### Перегляд поточної версії:
```bash
alembic current
```

## Використання репозиторіїв

Приклад використання дивіться в `src/database/example_usage.py`

### Основні методи:

**UserRepo:**
- `get_or_create_user()` - Створення або отримання користувача
- `get_user_by_id()` - Отримання користувача за ID
- `update_user_balance()` - Оновлення балансу
- `update_user_rating()` - Оновлення рейтингу
- `ban_user()` - Блокування користувача
- `mark_as_scammer()` - Позначення як шахрай

**PostRepo:**
- `create_post()` - Створення нового завдання
- `get_post_by_id()` - Отримання завдання за ID
- `get_public_feed()` - Отримання публічної стрічки
- `get_user_posts()` - Отримання завдань користувача
- `assign_executor()` - Призначення виконавця
- `update_status()` - Оновлення статусу
- `delete_post()` - Видалення завдання
