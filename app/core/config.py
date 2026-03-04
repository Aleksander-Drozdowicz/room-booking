from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://booking:booking@localhost:5432/booking"
    holiday_api_base_url: str = "https://date.nager.at/api/v3/PublicHolidays/2026/PL"

    class Config:
        env_file = ".env"

settings = Settings()