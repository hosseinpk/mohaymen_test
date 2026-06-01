from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import SecretStr

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):

    DB_URL: str
    REDIS_URL: str
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_LOG_TOPIC: str
    CACHE_TTL: int
    CACHE_MAX_ITEMS: int

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8",extra="ignore"
    )


settings = Settings()
