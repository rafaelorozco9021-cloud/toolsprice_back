from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    jwt_expire_minutes: int = 60
    redis_url: str = ""
    frontend_url: str = "http://localhost:5173"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
