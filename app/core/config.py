import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://booking:booking@localhost:5432/booking"
    holiday_api_base_url: str = "https://holiday.test"

    class Config:
        env_file = ".env"

# produkcyjne/local
settings = Settings()

# testowe (nadpisuje DB jeśli env jest ustawiony)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if TEST_DATABASE_URL:
    settings.database_url = TEST_DATABASE_URL