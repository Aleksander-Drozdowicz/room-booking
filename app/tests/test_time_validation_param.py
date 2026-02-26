import pytest
from datetime import datetime, timedelta, timezone

from app.domain.time_range import TimeRange


@pytest.mark.parametrize(
    "start_delta_hours,end_delta_hours,should_raise",
    [
        (10, 9, True),    # end < start
        (10, 10, True),   # zero length
        (10, 11, False),  # ok 1h
    ]
)
def test_time_range_validation_parametrized(start_delta_hours, end_delta_hours, should_raise):
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    start = now + timedelta(hours=start_delta_hours)
    end = now + timedelta(hours=end_delta_hours)

    tr = TimeRange(start=start, end=end)

    if should_raise:
        with pytest.raises(ValueError):
            tr.validate(max_duration=timedelta(hours=8))
    else:
        tr.validate(max_duration=timedelta(hours=8))