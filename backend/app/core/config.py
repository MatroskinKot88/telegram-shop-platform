from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/telegram_shop"
    BOT_TOKEN: str = "YOUR_BOT_TOKEN" # Временный токен для тестов
    
    class Config:
        env_file = ".env"

settings = Settings()