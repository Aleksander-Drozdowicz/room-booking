import os
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import Base, engine, SessionLocal
from app.domain.models import User, Room

pytestmark = pytest.mark.integration #wszystkie testy w tym pliku są oznaczone jako integracyjne


@pytest.fixture(scope="session", autouse=True)
def ensure_test_db(): # Sprawdza, czy masz ustawioną bazę danych.jezel nie , pomija testy integracyjne
    if not os.getenv("DATABASE_URL") and not os.getenv("TEST_DATABASE_URL"):
        pytest.skip(
            "Brak DATABASE_URL/TEST_DATABASE_URL - pomijam testy integracyjne",
            allow_module_level=True,
        )

    Base.metadata.create_all(bind=engine) #tworzy tabele w bazie (jeśli nie istnieją)
    yield 
    


@pytest.fixture(autouse=True)
def clean_db():
    
    with SessionLocal() as db:
        db.execute(text("TRUNCATE TABLE reservations RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE rooms RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        db.commit()
    yield
#Dzięki temu każdy test startuje na czystej bazie.

def test_db_can_insert_and_read_user_and_room():
    with SessionLocal() as db:  # otwieram polaczenie do bazy
        u = User(email="a@test.com")     
        r = Room(name="Room A")
        db.add_all([u, r])
        db.commit()
        db.refresh(u)
        db.refresh(r)

        u2 = db.query(User).filter_by(email="a@test.com").one() #odczytujesz z db uzytkownika po email
        r2 = db.query(Room).filter_by(name="Room A").one() #odczytujesz z db pokoj po nazwie

        assert u2.id == u.id #sprawdzam czy to ten sam rekord 
        assert r2.id == r.id
        #Ten test łączy się z prawdziwą bazą Postgres, dodaje do niej użytkownika i pokój, a potem sprawdza, czy da się ich odczytać (czyli czy zapis do DB działa).
