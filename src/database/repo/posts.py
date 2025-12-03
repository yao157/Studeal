from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.posts import Post
from src.database.models.users import User

class PostRepo:
    """
    Репозиторій для роботи з оголошеннями (Tasks/Posts).
    Всі запити до таблиці 'posts' проходять через цей клас.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(
        self, 
        author_id: int, 
        title: str, 
        description: str, 
        budget: Decimal, 
        category: str,
        post_type: str = "public"
    ) -> Post:
        """
        Створення нового завдання (спочатку статус 'draft' або 'moderation').
        """
        post = Post(
            author_id=author_id,
            title=title,
            description=description,
            budget=budget,
            category=category,
            post_type=post_type,
            status="draft"
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def get_post_by_id(self, post_id: UUID) -> Optional[Post]:
        """
        Отримання завдання за унікальним ID.
        Потрібно для відображення деталей або редагування.
        """
        stmt = select(Post).where(
            and_(Post.id == post_id, Post.deleted_at.is_(None))
        ).options(
            selectinload(Post.author),
            selectinload(Post.executor)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_public_feed(
        self, 
        limit: int = 10, 
        offset: int = 0, 
        category: str = None
    ) -> List[Post]:
        """
        Отримання списку активних завдань для 'Бота завдань'.
        Фільтрує тільки ті, що мають статус 'published'.
        """
        conditions = [
            Post.status == "published",
            Post.deleted_at.is_(None),
            Post.post_type == "public"
        ]
        
        if category:
            conditions.append(Post.category == category)
        
        stmt = select(Post).where(
            and_(*conditions)
        ).options(
            selectinload(Post.author)
        ).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_posts(
        self, 
        user_id: int, 
        status: str = None
    ) -> List[Post]:
        """
        Отримання історії постів конкретного користувача (для меню 'Мої замовлення').
        """
        conditions = [
            Post.author_id == user_id,
            Post.deleted_at.is_(None)
        ]
        
        if status:
            conditions.append(Post.status == status)
        
        stmt = select(Post).where(
            and_(*conditions)
        ).options(
            selectinload(Post.executor)
        ).order_by(Post.created_at.desc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def set_channel_message_id(
        self, 
        post_id: UUID, 
        message_id: int
    ) -> bool:
        """
        Зберігає ID повідомлення в каналі після успішної публікації.
        Необхідно для подальшого редагування кнопок під постом.
        """
        post = await self.get_post_by_id(post_id)
        if post:
            post.channel_message_id = message_id
            await self.session.commit()
            return True
        return False

    async def assign_executor(
        self, 
        post_id: UUID, 
        executor_id: int
    ) -> Optional[Post]:
        """
        Призначає виконавця на завдання та змінює статус на 'working'.
        Має містити перевірку, чи завдання ще вільне (Race Condition check).
        """
        post = await self.get_post_by_id(post_id)
        if not post:
            return None
        
        # Перевірка, чи завдання ще вільне (Race Condition)
        if post.status != "published" or post.executor_id is not None:
            return None
        
        post.executor_id = executor_id
        post.status = "working"
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_status(
        self, 
        post_id: UUID, 
        new_status: str
    ) -> Optional[Post]:
        """
        Зміна статусу (наприклад, на 'completed', 'archived' або 'dispute').
        Автоматично оновлює поле updated_at.
        """
        post = await self.get_post_by_id(post_id)
        if post:
            post.status = new_status
            await self.session.commit()
            await self.session.refresh(post)
            return post
        return None

    async def delete_post(self, post_id: UUID) -> bool:
        """
        М'яке видалення (архівування) або повне видалення чернетки.
        """
        from datetime import datetime, timezone
        
        post = await self.get_post_by_id(post_id)
        if post:
            if post.status == "draft":
                # Повне видалення чернетки
                await self.session.delete(post)
            else:
                # М'яке видалення (архівування)
                post.deleted_at = datetime.now(timezone.utc)
                post.status = "archived"
            await self.session.commit()
            return True
        return False

