from datetime import datetime, date, timezone
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.domain.models import Reservation, ReservationStatus


class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, r: Reservation) -> Reservation:
        self.db.add(r)
        self.db.flush()
        return r

    def get(self, reservation_id: int) -> Reservation | None:
        return self.db.query(Reservation).filter(Reservation.id == reservation_id).one_or_none()

    def count_user_reservations_on_day(self, user_id: int, day: date) -> int:
        day_start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        day_end = day_start.replace(hour=23, minute=59, second=59)

        return (
            self.db.query(Reservation)
            .filter(
                Reservation.user_id == user_id,
                Reservation.status == ReservationStatus.ACTIVE,
                Reservation.start >= day_start,
                Reservation.start <= day_end,
            )
            .count()
        )

    def has_conflict(self, room_id: int, start: datetime, end: datetime) -> bool:
        q = (
            self.db.query(Reservation) # tworzymy zapytanie na modelu reservation
            .filter( #przeszukujemy DB 
                Reservation.room_id == room_id,
                Reservation.status == ReservationStatus.ACTIVE,
                and_(Reservation.start < end, start < Reservation.end),
            )
        )
        return self.db.query(q.exists()).scalar() 