from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from pathlib import Path

import os




class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow environment variables to override .env file values
        env_ignore_empty=True
    )

    ANTHROPIC_KEY: SecretStr = Field(
        description="API key for Anthropic's language models",
        env="ANTHROPIC_KEY"
    )


Settings = Settings()