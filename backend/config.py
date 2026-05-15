from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM (env: GROQ_API_KEY; GROK_API_KEY accepted — common typo for "Groq")
    groq_api_key: str = Field(
        ...,
        validation_alias=AliasChoices("groq_api_key", "grok_api_key"),
    )
    llm_model: str = "llama-3.3-70b-versatile"

    # Google Drive
    google_sa_json_b64: str  # base64-encoded service account JSON
    drive_folder_id: str  # root folder to search within

    # App
    app_env: str = "development"
    backend_url: str = "http://localhost:8000"
    max_results: int = 20

@lru_cache()
def get_settings() -> Settings:
    return Settings()
