from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "ATTENDEE"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class EventCreate(BaseModel):
    event_name: str = Field(min_length=3, max_length=200)
    description: str = ""
    event_type: str = "Workshop"
    event_date: str
    start_time: str
    end_time: str
    venue: str = ""
    online_link: Optional[str] = None
    maximum_capacity: int = Field(gt=0, le=1000000)
    registration_deadline: str

class EventOut(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    organizer_id: int
    status: str
    created_at: datetime
    updated_at: datetime

class RSVPRequest(BaseModel):
    status: str

class RSVPOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: int
    user_id: int
    status: str
    responded_at: datetime
    updated_at: datetime

class AnnouncementCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    message: str = Field(min_length=2)

class AnnouncementOut(AnnouncementCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: int
    created_at: datetime

class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    event_id: Optional[int]
    type: str
    message: str
    read: bool
    created_at: datetime
