"""Обробники подій Task Bot: /start, реєстрація за контактом, головне меню."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bots.task_bot import keyboards, texts
from src.database.models.base import session_maker
from src.database.models.users import User
from src.database.repo.users import UserRepo

router = Router(name="task_bot")


def _is_registered(user: User | None) -> bool:
    """Перевіряє, чи користувач у БД і чи підтверджено номер телефону.

    Args:
        user: Запис користувача або ``None``.

    Returns:
        ``True``, якщо можна показувати головне меню.
    """
    return user is not None and user.phone is not None


def _display_name(message: Message) -> str:
    """Формує зручне повне ім'я з об'єкта Telegram-користувача.

    Args:
        message: Вхідне повідомлення бота.

    Returns:
        Рядок для поля ``full_name`` у базі.
    """
    u = message.from_user
    if not u:
        return ""
    parts = [u.first_name or "", u.last_name or ""]
    from_profile = " ".join(p for p in parts if p).strip()
    if from_profile:
        return from_profile
    return u.username or "Користувач"


def _full_name_from_contact(message: Message) -> str:
    """Ім'я з контакту або з профілю відправника.

    Args:
        message: Повідомлення з полем ``contact``.

    Returns:
        Рядок для збереження в ``User.full_name``.
    """
    c = message.contact
    if not c:
        return _display_name(message)
    from_contact = " ".join(
        p for p in (c.first_name, c.last_name) if p
    ).strip()
    if from_contact:
        return from_contact
    return _display_name(message)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Відповідає на /start: опис бота, реєстрація або головне меню."""
    if not message.from_user:
        return

    tid = message.from_user.id

    async with session_maker() as session:
        repo = UserRepo(session)
        user = await repo.get_user_by_id(tid)

        if user and user.is_banned:
            await message.answer(texts.USER_BANNED)
            return

        await message.answer(texts.WELCOME_ABOUT)

        if _is_registered(user):
            await message.answer(
                texts.MAIN_MENU_PROMPT,
                reply_markup=keyboards.main_menu_keyboard(),
            )
            return

        await message.answer(
            texts.ASK_SHARE_PHONE,
            reply_markup=keyboards.share_phone_keyboard(),
        )


@router.message(F.contact)
async def handle_contact(message: Message) -> None:
    """Приймає контакт Telegram і завершує реєстрацію (з перевіркою власника)."""
    if not message.from_user or not message.contact:
        return

    contact = message.contact
    if (
        contact.user_id is not None
        and contact.user_id != message.from_user.id
    ):
        await message.answer(texts.CONTACT_NOT_OWN)
        return

    tid = message.from_user.id
    phone = contact.phone_number
    username = message.from_user.username
    full_name = _full_name_from_contact(message)

    async with session_maker() as session:
        repo = UserRepo(session)
        existing = await repo.get_user_by_id(tid)
        if existing and existing.is_banned:
            await message.answer(texts.USER_BANNED)
            return

        await repo.get_or_create_user(
            telegram_id=tid,
            username=username,
            full_name=full_name,
            phone=phone,
        )

    await message.answer(
        texts.REGISTRATION_DONE,
        reply_markup=keyboards.main_menu_keyboard(),
    )


@router.message(F.text == keyboards.BTN_NEW_TASK)
async def menu_new_task(message: Message) -> None:
    """Заглушка для пункту «Нове завдання»."""
    if not message.from_user:
        return
    user = await _load_user(message.from_user.id)
    if not _is_registered(user):
        await message.answer(
            texts.CONTACT_NEEDED_FIRST,
            reply_markup=keyboards.share_phone_keyboard(),
        )
        return
    await message.answer(texts.PLACEHOLDER_NEW_TASK)


@router.message(F.text == keyboards.BTN_TASKS)
async def menu_tasks(message: Message) -> None:
    """Заглушка для пункту «Завдання»."""
    if not message.from_user:
        return
    user = await _load_user(message.from_user.id)
    if not _is_registered(user):
        await message.answer(
            texts.CONTACT_NEEDED_FIRST,
            reply_markup=keyboards.share_phone_keyboard(),
        )
        return
    await message.answer(texts.PLACEHOLDER_TASKS)


@router.message(F.text == keyboards.BTN_PROFILE)
async def menu_profile(message: Message) -> None:
    """Заглушка для пункту «Профіль»."""
    if not message.from_user:
        return
    user = await _load_user(message.from_user.id)
    if not _is_registered(user):
        await message.answer(
            texts.CONTACT_NEEDED_FIRST,
            reply_markup=keyboards.share_phone_keyboard(),
        )
        return
    await message.answer(texts.PLACEHOLDER_PROFILE)


async def _load_user(telegram_id: int) -> User | None:
    """Завантажує користувача з БД однією короткою сесією.

    Args:
        telegram_id: Ідентифікатор у Telegram.

    Returns:
        Модель ``User`` або ``None``.
    """
    async with session_maker() as session:
        repo = UserRepo(session)
        return await repo.get_user_by_id(telegram_id)
