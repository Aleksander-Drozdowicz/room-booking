from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
#konwertuje JSON → Python

class CreateReservationRequest(BaseModel):
    user_email: EmailStr #email musi byc poprawny 
    room_name: str = Field(min_length=1, max_length=255)
    start: datetime
    end: datetime


class ReservationResponse(BaseModel): #odpowiedz zwracana przez API 
    id: int
    user_id: int
    room_id: int
    start: datetime
    end: datetime
    status: str
    #to wszystko co uzytkownik dostanie w odp