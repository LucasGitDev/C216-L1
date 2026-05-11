from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "004 CRUD Alunos"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/students"
    database_url_test: str = "postgresql://postgres:postgres@localhost:5432/students_test"
    db_pool_min_size: int = 1
    db_pool_max_size: int = 10

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
