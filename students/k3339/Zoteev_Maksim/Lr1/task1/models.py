from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TravelStyle(str, Enum):
    active = "active"
    relaxed = "relaxed"
    budget = "budget"
    road_trip = "road_trip"


class UserProfile(BaseModel):
    id: int
    name: str
    age: int = Field(..., ge=18)
    city: str
    bio: str
    travel_style: TravelStyle
    languages: List[str] = Field(default_factory=list)


class TripStop(BaseModel):
    id: int
    location: str
    days: int = Field(..., ge=1)
    note: Optional[str] = None


class Trip(BaseModel):
    id: int
    title: str
    departure_city: str
    destination_city: str
    start_date: str
    end_date: str
    duration_days: int = Field(..., ge=1)
    description: str
    organizer: UserProfile
    stops: List[TripStop] = Field(default_factory=list)


class UserProfileCreate(BaseModel):
    name: str
    age: int = Field(..., ge=18)
    city: str
    bio: str
    travel_style: TravelStyle
    languages: List[str] = Field(default_factory=list)


class TripStopCreate(BaseModel):
    location: str
    days: int = Field(..., ge=1)
    note: Optional[str] = None


class TripCreate(BaseModel):
    title: str
    departure_city: str
    destination_city: str
    start_date: str
    end_date: str
    duration_days: int = Field(..., ge=1)
    description: str
    organizer_id: int
    stops: List[TripStopCreate] = Field(default_factory=list)
