"""App settings — env vars via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings and environment variables.

    Attributes:
        database_url (str): Connection string for the PostgreSQL database.
        fonnte_token (str): API token for the Fonnte WhatsApp integration.
        fonnte_base_url (str): Base URL for the Fonnte API.
        openai_api_key (str): API key for OpenAI services.
        jwt_secret (str): Secret key for encoding JSON Web Tokens.
        port (int): The port on which the server will run.
    """
    database_url: str = "postgresql+asyncpg://notaku:notaku@localhost:5432/notaku"
    fonnte_token: str = ""
    fonnte_base_url: str = "https://api.fonnte.com"
    openai_api_key: str = ""
    jwt_secret: str = "dev-secret-change-me"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
