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


@pytest.mark.asyncio#Jeśli dzień jest świętem, to nie da się utworzyć rezerwacji 
async def test_create_reservation_holiday_forbidden():
    db = MagicMock()
    repo = MagicMock()

    holiday_client = MagicMock()      #atrapa api zewnetrznego
    holiday_client.is_holiday = AsyncMock(return_value=True) #symulujemy ze data to swieto

    service = ReservationService(
        db=db,
        reservation_repo=repo,      #udawane repo db holiday
        holiday_client=holiday_client,
        now_fn=lambda: datetime(2030, 1, 1, tzinfo=timezone.utc), #now_fn funkcja co jest teraz
    )

    start = datetime(2030, 1, 10, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)#ustawiam rezerwacje od 10-11

    with pytest.raises(HolidayBookingForbiddenException):#musi to wypluc
        await service.create_reservation( 
            user_id=1,
            room_id=1, #parametry ktore przekazujemy do create reservation
            start=start,
            end=end,
        )
#Ten test udaje, że data jest świętem (mock zwraca True) i sprawdza, czy create_reservation wtedy rzuca wyjątek HolidayBookingForbiddenException.


@pytest.mark.asyncio #sprawdza limit dzienny rezerwacji użytkownika.
async def test_create_reservation_daily_limit():
    db = MagicMock()
    repo = MagicMock()
    

    repo.count_user_reservations_on_day.return_value = 2 # “symuluję, że user ma już 2 rezerwacje tego dnia”.

    holiday_client = MagicMock()
    holiday_client.is_holiday = AsyncMock(return_value=False) #Symulujesz, że to nie jest święto, żeby test nie wywalił się wcześniej na regule „nie rezerwuj w święto”.

    service = ReservationService( #Tworzysz obiekt ReservationService,i podajesz zmockowane zaleznosci
        db=db,
        reservation_repo=repo,
        holiday_client=holiday_client,
        now_fn=lambda: datetime(2030, 1, 1, tzinfo=timezone.utc),
    )

    start = datetime(2030, 1, 10, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)

    with pytest.raises(TooManyReservationsException): #Test przejdzie tylko wtedy, gdy kod w środku rzuci TooManyReservationsException.
        await service.create_reservation( #ma zakończyć się błędem — a nie sukcesem.(to poprostu - sprobuj zrobic rezerwacje)
            user_id=1,
            room_id=1,
            start=start,
            end=end, #Spróbuj utworzyć rezerwację dla usera 1,1 pokoju od x do y godziny
        )
#Ten test udaje repozytorium tak, żeby zwracało „użytkownik ma już 2 rezerwacje tego dnia” i sprawdza, czy serwis blokuje kolejną rezerwację wyjątkiem TooManyReservationsException.

@pytest.mark.asyncio #Jeśli w danym czasie pokój jest już zajęty → system ma rzucić ReservationConflictException.
async def test_create_reservation_conflict():
    db = MagicMock()
    repo = MagicMock()

    repo.count_user_reservations_on_day.return_value = 0 #User nie przekroczył limitu dziennego.
    repo.has_conflict.return_value = True

    holiday_client = MagicMock()
    holiday_client.is_holiday = AsyncMock(return_value=False) #czy to swieto - nie , nie zostanie zablokowana przez regule swieto

    service = ReservationService( #tworze reservation service
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
        #test udaje, że pokój ma już rezerwację w tym czasie