from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.domain.exceptions import (
    BookingValidationException,
    HolidayBookingForbiddenException,
    ReservationConflictException,
    TooManyReservationsException,
    TooLateToCancelException,
    ReservationNotFoundException,
)
from app.domain.models import Reservation, ReservationStatus
from app.domain.time_range import TimeRange
from app.infrastructure.holiday_client import HolidayApiClient
from app.repositories.reservation_repo import ReservationRepository


@dataclass
class ReservationPolicy:
    max_duration: timedelta = timedelta(hours=4)
    max_per_user_per_day: int = 2
    cancel_min_notice: timedelta = timedelta(minutes=30)


class ReservationService:
    def __init__(
        self,
        db: Session,
        reservation_repo: ReservationRepository,
        holiday_client: HolidayApiClient,
        policy: ReservationPolicy | None = None,
        now_fn=lambda: datetime.now(timezone.utc),
    ):
        self.db = db
        self.reservation_repo = reservation_repo
        self.holiday_client = holiday_client #przekazanie obiektu API
        self.policy = policy or ReservationPolicy()
        self.now_fn = now_fn

    async def create_reservation(self, *, user_id: int, room_id: int, start: datetime, end: datetime) -> Reservation:
        now = self.now_fn()

        if start.tzinfo is None or end.tzinfo is None:
            raise BookingValidationException("start/end must be timezone-aware")

        if start <= now:
            raise BookingValidationException("cannot book in the past")

        tr = TimeRange(start=start, end=end)
        try:
            tr.validate(max_duration=self.policy.max_duration)
        except ValueError as e:
            raise BookingValidationException(str(e)) from e

        if await self.holiday_client.is_holiday(start.date()):
            raise HolidayBookingForbiddenException("cannot book on a holiday")

        cnt = self.reservation_repo.count_user_reservations_on_day(user_id, start.date())
        if cnt >= self.policy.max_per_user_per_day:
            raise TooManyReservationsException("daily limit exceeded")

        if self.reservation_repo.has_conflict(room_id, start, end):
            raise ReservationConflictException("time conflict")

        r = Reservation(
            user_id=user_id,
            room_id=room_id,
            start=start,
            end=end,
            status=ReservationStatus.ACTIVE,
            created_at=now,
        )
        self.reservation_repo.add(r)
        self.db.commit()
        self.db.refresh(r)
        return r

    def cancel_reservation(self, *, reservation_id: int, user_id: int) -> Reservation:
        r = self.reservation_repo.get(reservation_id)
        if not r:
            raise ReservationNotFoundException("reservation not found")
        if r.user_id != user_id:
            raise ReservationNotFoundException("reservation not found")

        now = self.now_fn()
        if (r.start - now) < self.policy.cancel_min_notice:
            raise TooLateToCancelException("too late to cancel")

        r.status = ReservationStatus.CANCELLED
        self.db.commit()#zatwierdza
        self.db.refresh(r)
        return r