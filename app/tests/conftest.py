import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base, get_db
from app.main import app


TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://booking:booking@localhost:5432/booking_test",
)


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DB_URL, pool_pre_ping=True) #tworzy polaczenie z testowa db i tabele 
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine) #usuwa tabele po zakonczeniu testow


@pytest.fixture() # Daje testowi dostęp do bazy i automatycznie sprzata po nim 
def db_session(engine):
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db #Zamiast prawdziwego get_db, użyj override_get_db
    with TestClient(app) as c: #To tworzy klienta HTTP
        yield c
    app.dependency_overrides.clear() #Po zakończeniu testu usuwa podmianę.