from datetime import date
from enum import Enum
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


class TravelStyle(str, Enum):
    active = "active"
    relaxed = "relaxed"
    budget = "budget"
    road_trip = "road_trip"


class ParticipantStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"


class UserProfileBase(SQLModel):
    name: str
    age: int = Field(ge=18)
    city: str
    bio: str
    travel_style: TravelStyle
    languages: list[str] = Field(
        default_factory=list, sa_column=Column(JSON, nullable=False)
    )


class UserProfile(UserProfileBase, table=True):
    __tablename__ = "user_profiles"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)

    trips_created: list["Trip"] = Relationship(back_populates="organizer")
    trip_links: list["TripParticipantLink"] = Relationship(
        back_populates="traveler",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    interest_links: list["UserInterestLink"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class InterestBase(SQLModel):
    name: str
    description: str


class Interest(InterestBase, table=True):
    __tablename__ = "interests"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)

    user_links: list["UserInterestLink"] = Relationship(
        back_populates="interest",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TripBase(SQLModel):
    title: str
    departure_city: str
    destination_city: str
    start_date: date
    end_date: date
    duration_days: int = Field(ge=1)
    description: str


class Trip(TripBase, table=True):
    __tablename__ = "trips"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    organizer_id: Optional[int] = Field(default=None, foreign_key="user_profiles.id")

    organizer: Optional["UserProfile"] = Relationship(back_populates="trips_created")
    stops: list["TripStop"] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    participant_links: list["TripParticipantLink"] = Relationship(
        back_populates="trip",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class TripStopBase(SQLModel):
    location: str
    days: int = Field(ge=1)
    note: Optional[str] = None


class TripStop(TripStopBase, table=True):
    __tablename__ = "trip_stops"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trips.id")

    trip: Optional["Trip"] = Relationship(back_populates="stops")


class TripParticipantLinkBase(SQLModel):
    status: ParticipantStatus = ParticipantStatus.pending
    note: Optional[str] = None


class TripParticipantLink(TripParticipantLinkBase, table=True):
    __tablename__ = "trip_participants"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: Optional[int] = Field(default=None, foreign_key="trips.id")
    traveler_id: Optional[int] = Field(default=None, foreign_key="user_profiles.id")

    trip: Optional["Trip"] = Relationship(back_populates="participant_links")
    traveler: Optional["UserProfile"] = Relationship(back_populates="trip_links")


class UserInterestLinkBase(SQLModel):
    experience_level: str = Field(default="beginner")


class UserInterestLink(UserInterestLinkBase, table=True):
    __tablename__ = "user_interests"  # type: ignore[assignment]

    user_id: Optional[int] = Field(
        default=None, foreign_key="user_profiles.id", primary_key=True
    )
    interest_id: Optional[int] = Field(
        default=None, foreign_key="interests.id", primary_key=True
    )

    user: Optional["UserProfile"] = Relationship(back_populates="interest_links")
    interest: Optional["Interest"] = Relationship(back_populates="user_links")


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(SQLModel):
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=18)
    city: Optional[str] = None
    bio: Optional[str] = None
    travel_style: Optional[TravelStyle] = None
    languages: Optional[list[str]] = None


class UserProfileRead(UserProfileBase):
    id: int


class InterestCreate(InterestBase):
    pass


class InterestUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None


class InterestRead(InterestBase):
    id: int


class TripCreate(TripBase):
    organizer_id: int


class TripUpdate(SQLModel):
    title: Optional[str] = None
    departure_city: Optional[str] = None
    destination_city: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    duration_days: Optional[int] = Field(default=None, ge=1)
    description: Optional[str] = None
    organizer_id: Optional[int] = None


class TripRead(TripBase):
    id: int
    organizer_id: int


class TripStopCreate(TripStopBase):
    pass


class TripStopUpdate(SQLModel):
    location: Optional[str] = None
    days: Optional[int] = Field(default=None, ge=1)
    note: Optional[str] = None


class TripStopRead(TripStopBase):
    id: int
    trip_id: int


class TripParticipantLinkCreate(TripParticipantLinkBase):
    traveler_id: int


class TripParticipantLinkUpdate(SQLModel):
    status: Optional[ParticipantStatus] = None
    note: Optional[str] = None


class TripParticipantLinkRead(TripParticipantLinkBase):
    id: int
    trip_id: int
    traveler_id: int


class UserInterestLinkCreate(UserInterestLinkBase):
    interest_id: int


class UserInterestLinkRead(UserInterestLinkBase):
    interest: InterestRead


class TripParticipantDetails(SQLModel):
    id: int
    status: ParticipantStatus
    note: Optional[str] = None
    traveler: UserProfileRead


class TripDetails(TripRead):
    organizer: UserProfileRead
    stops: list[TripStopRead] = Field(default_factory=list)
    participants: list[TripParticipantDetails] = Field(default_factory=list)


class JoinedTripRead(SQLModel):
    participant_id: int
    status: ParticipantStatus
    note: Optional[str] = None
    trip: TripRead


class UserProfileDetails(UserProfileRead):
    interests: list[UserInterestLinkRead] = Field(default_factory=list)
    created_trips: list[TripRead] = Field(default_factory=list)
    joined_trips: list[JoinedTripRead] = Field(default_factory=list)
