from sqlalchemy.orm import Session
from app.domain.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_by_email(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email).one_or_none()
        if user:
            return user
        user = User(email=email)
        self.db.add(user)   #dodaje
        self.db.flush()#wysyla dane do bazy bez zatwierdzenia,(services zatwierdza)(Repozytorium nie powinno samo decydować o commit)
        return user