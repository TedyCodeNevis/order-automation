# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    #Base url
    BASE_URL: str = ""

    # Panel
    PANEL_URL: str = ""
    PANEL_USERNAME: str = ""
    PANEL_PASSWORD: str = ""

    # Telegram
    BOT_TOKEN: str
    CHAT_ID: str

    # General
    LOG_LEVEL: str = "INFO"


settings = Settings()