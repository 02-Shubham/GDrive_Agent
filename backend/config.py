from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # LLM
    groq_api_key: str
    llm_model: str = "llama-3.3-70b-versatile"
    
    # Google Drive
    google_sa_json_b64: str          # base64-encoded service account JSON
    drive_folder_id: str             # root folder to search within
    
    # App
    app_env: str = "development"
    backend_url: str = "http://localhost:8000"
    max_results: int = 10
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
