from sqlalchemy.orm import Session
from app.domain.models import Room


class RoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_by_name(self, name: str) -> Room:
        room = self.db.query(Room).filter(Room.name == name).one_or_none()
        if room:
            return room
        room = Room(name=name)
        self.db.add(room)
        self.db.flush()
        return room