from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel

from app.models.enums import TravelStyle

if TYPE_CHECKING:
    from app.models.interest import UserInterestLink
    from app.models.trip import Trip, TripParticipantLink


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    full_name: str
    age: int = Field(ge=18)
    city: str
    bio: Optional[str] = None
    travel_style: TravelStyle
    telegram_username: Optional[str] = None
    languages: list[str] = Field(
        default_factory=list,
        sa_column=Column(JSON, nullable=False),
    )


class User(UserBase, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str

    created_trips: list["Trip"] = Relationship(
        back_populates="organizer",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    interest_links: list["UserInterestLink"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    trip_participations: list["TripParticipantLink"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
