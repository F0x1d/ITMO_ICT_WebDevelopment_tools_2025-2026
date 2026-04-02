from enum import Enum


class TravelStyle(str, Enum):
    active = "active"
    relaxed = "relaxed"
    budget = "budget"
    road_trip = "road_trip"


class ParticipantStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"
