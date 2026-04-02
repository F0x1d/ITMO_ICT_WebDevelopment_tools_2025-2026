from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import ParticipantStatus


class TripCreate(BaseModel):
    title: str
    departure_city: str
    destination_city: str
    start_date: date
    end_date: date
    duration_days: int
    description: str


class TripUpdate(BaseModel):
    title: str | None = None
    departure_city: str | None = None
    destination_city: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    duration_days: int | None = None
    description: str | None = None


class TripShortRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    departure_city: str
    destination_city: str
    start_date: date
    end_date: date
    duration_days: int
    description: str
    organizer_id: int


class TripStopCreate(BaseModel):
    location: str
    days: int
    note: str | None = None


class TripStopUpdate(BaseModel):
    location: str | None = None
    days: int | None = None
    note: str | None = None


class TripStopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    location: str
    days: int
    note: str | None = None


class TripParticipantCreate(BaseModel):
    user_id: int
    status: ParticipantStatus = ParticipantStatus.pending
    message: str | None = None
    contact_preference: str | None = None


class TripParticipantUpdate(BaseModel):
    status: ParticipantStatus | None = None
    message: str | None = None
    contact_preference: str | None = None


class TripParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    user_id: int
    status: ParticipantStatus
    message: str | None = None
    contact_preference: str | None = None


class TripParticipantDetails(BaseModel):
    id: int
    status: ParticipantStatus
    message: str | None = None
    contact_preference: str | None = None
    user: UserRead


class TripDetails(TripShortRead):
    organizer: UserRead
    stops: list[TripStopRead]
    participants: list[TripParticipantDetails]


from app.schemas.user import UserRead

TripParticipantDetails.model_rebuild()
TripDetails.model_rebuild()
