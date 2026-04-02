from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import ParticipantStatus

if TYPE_CHECKING:
    from app.models.user import User


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
    organizer_id: int = Field(foreign_key="users.id")

    organizer: Optional["User"] = Relationship(back_populates="created_trips")
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
    trip_id: int = Field(foreign_key="trips.id")

    trip: Optional["Trip"] = Relationship(back_populates="stops")


class TripParticipantLinkBase(SQLModel):
    status: ParticipantStatus = ParticipantStatus.pending
    message: Optional[str] = None
    contact_preference: Optional[str] = None


class TripParticipantLink(TripParticipantLinkBase, table=True):
    __tablename__ = "trip_participants"  # type: ignore[assignment]
    __table_args__ = (
        UniqueConstraint("trip_id", "user_id", name="uq_trip_participant"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trips.id")
    user_id: int = Field(foreign_key="users.id")

    trip: Optional["Trip"] = Relationship(back_populates="participant_links")
    user: Optional["User"] = Relationship(back_populates="trip_participations")
