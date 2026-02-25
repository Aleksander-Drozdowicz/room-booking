from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class CreateReservationRequest(BaseModel):
    user_email: EmailStr
    room_name: str = Field(min_length=1, max_length=255)
    start: datetime
    end: datetime


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    start: datetime
    end: datetime
    status: str