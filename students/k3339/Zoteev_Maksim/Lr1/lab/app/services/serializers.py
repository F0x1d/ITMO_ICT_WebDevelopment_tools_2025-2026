from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from typing import Any, cast

from app.models import Interest, Trip, TripParticipantLink, User, UserInterestLink
from app.schemas.interest import InterestRead, UserInterestRead
from app.schemas.trip import (
    TripDetails,
    TripParticipantDetails,
    TripShortRead,
    TripStopRead,
)
from app.schemas.user import JoinedTripRead, UserDetails, UserRead


def get_user_with_details(session: Session, user_id: int) -> User:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(cast(Any, User.interest_links)).selectinload(
                cast(Any, UserInterestLink.interest)
            ),
            selectinload(cast(Any, User.created_trips)),
            selectinload(cast(Any, User.trip_participations)).selectinload(
                cast(Any, TripParticipantLink.trip)
            ),
        )
    )
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_trip_with_details(session: Session, trip_id: int) -> Trip:
    statement = (
        select(Trip)
        .where(Trip.id == trip_id)
        .options(
            selectinload(cast(Any, Trip.organizer)),
            selectinload(cast(Any, Trip.stops)),
            selectinload(cast(Any, Trip.participant_links)).selectinload(
                cast(Any, TripParticipantLink.user)
            ),
        )
    )
    trip = session.exec(statement).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def serialize_user_details(user: User) -> UserDetails:
    if user.id is None:
        raise HTTPException(status_code=500, detail="User data is incomplete")

    return UserDetails(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        age=user.age,
        city=user.city,
        bio=user.bio,
        travel_style=user.travel_style,
        telegram_username=user.telegram_username,
        languages=user.languages,
        interests=[
            UserInterestRead(
                interest=InterestRead.model_validate(link.interest),
                experience_level=link.experience_level,
            )
            for link in user.interest_links
            if link.interest is not None
        ],
        created_trips=[
            TripShortRead.model_validate(trip) for trip in user.created_trips
        ],
        joined_trips=[
            JoinedTripRead(
                participant_id=link.id or 0,
                status=link.status.value,
                message=link.message,
                contact_preference=link.contact_preference,
                trip=TripShortRead.model_validate(link.trip),
            )
            for link in user.trip_participations
            if link.trip is not None
        ],
    )


def serialize_trip_details(trip: Trip) -> TripDetails:
    if trip.id is None or trip.organizer is None:
        raise HTTPException(status_code=500, detail="Trip data is incomplete")

    return TripDetails(
        id=trip.id,
        title=trip.title,
        departure_city=trip.departure_city,
        destination_city=trip.destination_city,
        start_date=trip.start_date,
        end_date=trip.end_date,
        duration_days=trip.duration_days,
        description=trip.description,
        organizer_id=trip.organizer_id,
        organizer=UserRead.model_validate(trip.organizer),
        stops=[TripStopRead.model_validate(stop) for stop in trip.stops],
        participants=[
            TripParticipantDetails(
                id=link.id or 0,
                status=link.status,
                message=link.message,
                contact_preference=link.contact_preference,
                user=UserRead.model_validate(link.user),
            )
            for link in trip.participant_links
            if link.user is not None
        ],
    )
