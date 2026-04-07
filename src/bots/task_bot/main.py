"""Точка входу Task Bot: polling через aiogram."""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from src.bots.task_bot.handlers import router


async def main() -> None:
    """Налаштовує логування, бота та диспетчер; запускає нескінченний polling."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    bot = Bot(
        token=config.bot.token_task.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
