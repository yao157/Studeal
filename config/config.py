from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbConfig(BaseModel):
    """Налаштування бази даних PostgreSQL (з .env лише через префікс DB__)."""

    host: str
    port: int = 5432
    user: str
    password: SecretStr
    name: str

    # Автоматично збирає DSN рядок (посилання на БД)
    # Використовуємо асинхронний драйвер postgresql+asyncpg
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"

class RedisConfig(BaseModel):
    """Налаштування Redis (для FSM та кешу); опційно через REDIS__*."""

    host: str = "localhost"
    port: int = 6379
    db_fsm: int = 0  # База для станів діалогів
    db_job: int = 1  # База для черги задач

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db_fsm}"

class BotConfig(BaseModel):
    """Налаштування Telegram ботів (BOT__* у .env)."""

    token_main: SecretStr  # Токен основного бота
    token_task: SecretStr  # Токен бота завдань
    admin_ids: list[int]   # Список ID адмінів
    channel_id: int        # ID каналу-вітрини

class Settings(BaseSettings):
    """Головний клас налаштувань"""

    db: DbConfig
    redis: RedisConfig = RedisConfig()
    bot: BotConfig

    # Вказуємо, звідки читати змінні (.env файл)
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__", # Дозволяє писати DB__HOST замість просто HOST
        case_sensitive=False
    )

# Ініціалізуємо об'єкт налаштувань один раз
config = Settings()