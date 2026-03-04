import pytest
from datetime import datetime, timedelta, timezone #operacja na czasie

from app.domain.time_range import TimeRange #time range - moja klasa biznesowa


@pytest.mark.parametrize(#uruchomi ten test kilka razy z roznymi danymi
    "start_delta_hours,end_delta_hours,should_raise",
    [
        (10, 9, True),    # end < start
        (10, 10, True),   # zero length
        (10, 11, False),  # ok 1h
    ]
)
def test_time_range_validation_parametrized(start_delta_hours, end_delta_hours, should_raise):
    now = datetime(2030, 1, 1, tzinfo=timezone.utc) ##Tworze punkt odniesienia czasu
    start = now + timedelta(hours=start_delta_hours) #jeżeli delta = 10 → godzina 10:00
    end = now + timedelta(hours=end_delta_hours)

    tr = TimeRange(start=start, end=end) #obiekt reprezentujacy zakres czasu

    if should_raise: 

        with pytest.raises(ValueError): #Jeśli w parametrach jest True: oczekuemy valueerror
            tr.validate(max_duration=timedelta(hours=8))
    else:
        tr.validate(max_duration=timedelta(hours=8))

        #To jest test parametryzowany, który sprawdza różne przypadki walidacji zakresu czasu