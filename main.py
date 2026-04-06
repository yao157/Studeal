"""Кореневий запуск застосунку: Task Bot."""

import asyncio

from src.bots.task_bot.main import main as run_task_bot


if __name__ == "__main__":
    asyncio.run(run_task_bot())
