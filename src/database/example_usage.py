"""
Приклад використання моделей та репозиторіїв.

Цей файл демонструє, як працювати з базою даних через репозиторії.
"""

from src.database.models.base import session_maker
from src.database.repo.users import UserRepo
from src.database.repo.posts import PostRepo
from decimal import Decimal

async def example_usage():
    """Приклад використання репозиторіїв"""
    
    async with session_maker() as session:
        # Робота з користувачами
        user_repo = UserRepo(session)
        
        # Створення або отримання користувача
        user = await user_repo.get_or_create_user(
            telegram_id=123456789,
            username="test_user",
            full_name="Test User",
            role="user"
        )
        print(f"Користувач: {user}")
        
        # Оновлення балансу
        await user_repo.update_user_balance(user.telegram_id, 100.50)
        
        # Робота з завданнями
        post_repo = PostRepo(session)
        
        # Створення нового завдання
        post = await post_repo.create_post(
            author_id=user.telegram_id,
            title="Test Task",
            description="Опис завдання",
            budget=Decimal("100.00"),
            category="programming",
            post_type="public"
        )
        print(f"Створено завдання: {post}")
        
        # Отримання завдання за ID
        found_post = await post_repo.get_post_by_id(post.id)
        print(f"Знайдено завдання: {found_post}")
        
        # Отримання публічної стрічки
        feed = await post_repo.get_public_feed(limit=10, offset=0)
        print(f"Знайдено завдань у стрічці: {len(feed)}")
        
        # Отримання завдань користувача
        user_posts = await post_repo.get_user_posts(user.telegram_id)
        print(f"Завдань користувача: {len(user_posts)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())

