from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.models.enums import TravelStyle
from app.schemas.interest import UserInterestRead


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    full_name: str
    age: int
    city: str
    bio: str | None = None
    travel_style: TravelStyle
    telegram_username: str | None = None
    languages: list[str]


class UserUpdate(BaseModel):
    username: str | None = None
    full_name: str | None = None
    age: int | None = None
    city: str | None = None
    bio: str | None = None
    travel_style: TravelStyle | None = None
    telegram_username: str | None = None
    languages: list[str] | None = None


class JoinedTripRead(BaseModel):
    participant_id: int
    status: str
    message: str | None = None
    contact_preference: str | None = None
    trip: TripShortRead


class UserDetails(UserRead):
    interests: list[UserInterestRead]
    created_trips: list[TripShortRead]
    joined_trips: list[JoinedTripRead]


from app.schemas.trip import TripShortRead

JoinedTripRead.model_rebuild()
UserDetails.model_rebuild()
