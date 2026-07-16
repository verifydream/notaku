"""App settings — env vars via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://notaku:notaku@localhost:5432/notaku"
    fonnte_token: str = ""
    fonnte_base_url: str = "https://api.fonnte.com"
    openai_api_key: str = ""
    jwt_secret: str = "dev-secret-change-me"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
