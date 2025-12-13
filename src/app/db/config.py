from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # Асинхронный вариант
    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+asyncpg://us_api_db:pas_api_db@localhost:5432/api_db
        # return f"postgresql+asyncpg://us_api_db:pas_api_db@localhost:5432/api_db"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # Синхронный вариант
    @property
    def DATABASE_URL_psycopg(self):
        # postgresql+psycopg://us_api_db:pas_api_db@localhost:5432/api_db
        # return f"postgresql+psycopg://us_api_db:pas_api_db@localhost:5432/api_db"
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"))


settings = Settings()
