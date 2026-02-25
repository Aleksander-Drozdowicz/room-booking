import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

from app.services.reservation_service import ReservationService
from app.domain.exceptions import (
    HolidayBookingForbiddenException,
    TooManyReservationsException,
    ReservationConflictException,
)
from app.domain.models import ReservationStatus


@pytest.mark.asyncio
async def test_create_reservation_holiday_forbidden():
    db = MagicMock()
    repo = MagicMock()

    holiday_client = MagicMock()
    holiday_client.is_holiday = AsyncMock(return_value=True)

    service = ReservationService(
        db=db,
        reservation_repo=repo,
        holiday_client=holiday_client,
        now_fn=lambda: datetime(2030, 1, 1, tzinfo=timezone.utc),
    )

    start = datetime(2030, 1, 10, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)

    with pytest.raises(HolidayBookingForbiddenException):
        await service.create_reservation(
            user_id=1,
            room_id=1,
            start=start,
            end=end,
        )


@pytest.mark.asyncio
async def test_create_reservation_daily_limit():
    db = MagicMock()
    repo = MagicMock()

    repo.count_user_reservations_on_day.return_value = 2

    holiday_client = MagicMock()
    holiday_client.is_holiday = AsyncMock(return_value=False)

    service = ReservationService(
        db=db,
        reservation_repo=repo,
        holiday_client=holiday_client,
        now_fn=lambda: datetime(2030, 1, 1, tzinfo=timezone.utc),
    )

    start = datetime(2030, 1, 10, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)

    with pytest.raises(TooManyReservationsException):
        await service.create_reservation(
            user_id=1,
            room_id=1,
            start=start,
            end=end,
        )


@pytest.mark.asyncio
async def test_create_reservation_conflict():
    db = MagicMock()
    repo = MagicMock()

    repo.count_user_reservations_on_day.return_value = 0
    repo.has_conflict.return_value = True

    holiday_client = MagicMock()
    holiday_client.is_holiday = AsyncMock(return_value=False)

    service = ReservationService(
        db=db,
        reservation_repo=repo,
        holiday_client=holiday_client,
        now_fn=lambda: datetime(2030, 1, 1, tzinfo=timezone.utc),
    )

    start = datetime(2030, 1, 10, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)

    with pytest.raises(ReservationConflictException):
        await service.create_reservation(
            user_id=1,
            room_id=1,
            start=start,
            end=end,
        )