from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.domain.exceptions import (
    BookingValidationException,
    HolidayBookingForbiddenException,
    ReservationConflictException,
    TooManyReservationsException,
    TooLateToCancelException,
    ReservationNotFoundException,
)
from app.infrastructure.holiday_client import HolidayApiClient
from app.repositories.reservation_repo import ReservationRepository
from app.repositories.room_repo import RoomRepository
from app.repositories.user_repo import UserRepository
from app.services.reservation_service import ReservationService
from app.api.schemas import CreateReservationRequest, ReservationResponse

router = APIRouter()


def to_response(r) -> ReservationResponse:
    return ReservationResponse(
        id=r.id,
        user_id=r.user_id,
        room_id=r.room_id,
        start=r.start,
        end=r.end,
        status=str(r.status),
    )


@router.post("/reservations", response_model=ReservationResponse) #1 endpoint API 
async def create_reservation(req: CreateReservationRequest, db: Session = Depends(get_db)):
    user = UserRepository(db).get_or_create_by_email(req.user_email)
    room = RoomRepository(db).get_or_create_by_name(req.room_name)
   

    service = ReservationService(
        db=db,
        reservation_repo=ReservationRepository(db),
        holiday_client=HolidayApiClient(settings.holiday_api_base_url),#tworzy obiekt ktory umozliwi nam dostep do zewnetrznego API 
    )

    try:
        r = await service.create_reservation(user_id=user.id, room_id=room.id, start=req.start, end=req.end)
        return to_response(r)
    except HolidayBookingForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except (TooManyReservationsException, ReservationConflictException, BookingValidationException) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reservations/{reservation_id}/cancel", response_model=ReservationResponse)
def cancel_reservation(reservation_id: int, user_email: str, db: Session = Depends(get_db)):
    user = UserRepository(db).get_or_create_by_email(user_email)

    service = ReservationService(
        db=db,
        reservation_repo=ReservationRepository(db),
        holiday_client=HolidayApiClient(settings.holiday_api_base_url),
    )

    try:
        r = service.cancel_reservation(reservation_id=reservation_id, user_id=user.id)
        return to_response(r)
    except TooLateToCancelException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ReservationNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))