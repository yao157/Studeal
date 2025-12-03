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

2. Створіть файл `.env` з налаштуваннями:
```
DB__HOST=localhost
DB__PORT=5432
DB__USER=your_user
DB__PASSWORD=your_password
DB__NAME=studeal_db
```

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
