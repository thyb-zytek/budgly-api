import secrets
from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )
    PROJECT_NAME: str
    DESCRIPTION: str
    VERSION: str

    API_STR: str = "/api/v"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = ENVIRONMENT != "production"

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SSL_MODE: bool = False

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
            query="sslmode=require" if self.POSTGRES_SSL_MODE else None,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
