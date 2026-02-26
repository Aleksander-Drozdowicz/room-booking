import os
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import Base, engine, SessionLocal
from app.domain.models import User, Room

pytestmark = pytest.mark.integration


@pytest.fixture(scope="session", autouse=True)
def ensure_test_db():
    if not os.getenv("DATABASE_URL") and not os.getenv("TEST_DATABASE_URL"):
        pytest.skip(
            "Brak DATABASE_URL/TEST_DATABASE_URL - pomijam testy integracyjne",
            allow_module_level=True,
        )

    Base.metadata.create_all(bind=engine)
    yield
    # opcjonalnie: nie usuwamy tabel, bo to testowa baza w dockerze


@pytest.fixture(autouse=True)
def clean_db():
    # czyść tabele przed każdym testem
    with SessionLocal() as db:
        db.execute(text("TRUNCATE TABLE reservations RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE rooms RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        db.commit()
    yield


def test_db_can_insert_and_read_user_and_room():
    with SessionLocal() as db:  # type: Session
        u = User(email="a@test.com")
        r = Room(name="Room A")
        db.add_all([u, r])
        db.commit()
        db.refresh(u)
        db.refresh(r)

        u2 = db.query(User).filter_by(email="a@test.com").one()
        r2 = db.query(Room).filter_by(name="Room A").one()

        assert u2.id == u.id
        assert r2.id == r.id
        