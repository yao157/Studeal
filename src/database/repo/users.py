from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.users import User

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        full_name: str = "",
        role: str = "user",
        phone: str | None = None,
    ) -> User:
        """Реєструє користувача, якщо його немає; оновлює профіль при конфлікті.

        Args:
            telegram_id: Ідентифікатор користувача в Telegram.
            username: Юзернейм без @; може бути None.
            full_name: Повне ім'я для відображення.
            role: Роль у системі (наприклад, ``user`` або ``admin``).
            phone: Номер телефону після надсилання контакту.

        Returns:
            Актуальний запис користувача з бази.
        """
        set_on_update = dict(username=username, full_name=full_name)
        if phone is not None:
            set_on_update["phone"] = phone

        stmt = (
            insert(User)
            .values(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                role=role,
                phone=phone,
                balance=Decimal("0"),
                rating=0.0,
            )
            .on_conflict_do_update(
                index_elements=[User.telegram_id],
                set_=set_on_update,
            )
            .returning(User)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one()

    async def get_user_by_id(self, telegram_id: int) -> Optional[User]:
        """Отримання користувача за Telegram ID"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_user_balance(self, telegram_id: int, new_balance: float) -> bool:
        """Оновлення балансу користувача"""
        user = await self.get_user_by_id(telegram_id)
        if user:
            user.balance = new_balance
            await self.session.commit()
            return True
        return False

    async def update_user_rating(self, telegram_id: int, new_rating: float) -> bool:
        """Оновлення рейтингу користувача"""
        user = await self.get_user_by_id(telegram_id)
        if user:
            user.rating = new_rating
            await self.session.commit()
            return True
        return False

    async def ban_user(self, telegram_id: int) -> bool:
        """Заблокувати користувача"""
        user = await self.get_user_by_id(telegram_id)
        if user:
            user.is_banned = True
            await self.session.commit()
            return True
        return False

    async def mark_as_scammer(self, telegram_id: int) -> bool:
        """Позначити користувача як шахрая"""
        user = await self.get_user_by_id(telegram_id)
        if user:
            user.is_scammer = True
            await self.session.commit()
            return True
        return False

