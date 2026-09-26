from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./event_tracker.db"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

def cors_list():
    return [x.strip() for x in settings.cors_origins.split(",") if x.strip()]
