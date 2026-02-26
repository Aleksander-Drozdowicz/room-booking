import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg://booking:booking@localhost:5432/booking",
    )
    holiday_api_base_url: str = os.getenv("HOLIDAY_API_BASE_URL", "https://holiday.test")

    class Config:
        env_file = ".env"

settings = Settings()