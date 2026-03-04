from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class TimeRange:
    start: datetime
    end: datetime

    def validate(self, *, max_duration: timedelta) -> None: #Sprawdza czy zakres czasu jest poprawny.
        if self.start >= self.end:
            raise ValueError("start must be before end")
        if (self.end - self.start) > max_duration: # rezerwacja dłuższa niż np. 8h → błąd
            raise ValueError("range too long")

    def overlaps(self, other: "TimeRange") -> bool:
        return self.start < other.end and other.start < self.end