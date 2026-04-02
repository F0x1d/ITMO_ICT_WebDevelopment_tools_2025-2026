from typing import Any, cast

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from connection import get_session
from models import (
    Interest,
    InterestCreate,
    InterestRead,
    InterestUpdate,
    JoinedTripRead,
    Trip,
    TripCreate,
    TripDetails,
    TripParticipantDetails,
    TripParticipantLink,
    TripParticipantLinkCreate,
    TripParticipantLinkRead,
    TripParticipantLinkUpdate,
    TripRead,
    TripStop,
    TripStopCreate,
    TripStopRead,
    TripStopUpdate,
    TripUpdate,
    UserInterestLink,
    UserInterestLinkCreate,
    UserInterestLinkRead,
    UserProfile,
    UserProfileCreate,
    UserProfileDetails,
    UserProfileRead,
    UserProfileUpdate,
)

app = FastAPI(title="Travel Buddy Finder Project Structure API")


def get_profile_or_404(session: Session, profile_id: int) -> UserProfile:
    profile = session.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def get_interest_or_404(session: Session, interest_id: int) -> Interest:
    interest = session.get(Interest, interest_id)
    if not interest:
        raise HTTPException(status_code=404, detail="Interest not found")
    return interest


def get_trip_or_404(session: Session, trip_id: int) -> Trip:
    trip = session.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def get_trip_stop_or_404(session: Session, stop_id: int) -> TripStop:
    stop = session.get(TripStop, stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Trip stop not found")
    return stop


def get_participant_link_or_404(session: Session, link_id: int) -> TripParticipantLink:
    link = session.get(TripParticipantLink, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Participant link not found")
    return link


def serialize_trip_details(trip: Trip) -> TripDetails:
    if trip.id is None or trip.organizer_id is None or trip.organizer is None:
        raise HTTPException(status_code=500, detail="Trip relation data is incomplete")

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
        organizer=UserProfileRead.model_validate(trip.organizer),
        stops=[TripStopRead.model_validate(stop) for stop in trip.stops],
        participants=[
            TripParticipantDetails(
                id=link.id or 0,
                status=link.status,
                note=link.note,
                contact_preference=link.contact_preference,
                traveler=UserProfileRead.model_validate(link.traveler),
            )
            for link in trip.participant_links
        ],
    )


def serialize_profile_details(profile: UserProfile) -> UserProfileDetails:
    if profile.id is None:
        raise HTTPException(status_code=500, detail="Profile data is incomplete")

    return UserProfileDetails(
        id=profile.id,
        name=profile.name,
        age=profile.age,
        city=profile.city,
        bio=profile.bio,
        travel_style=profile.travel_style,
        languages=profile.languages,
        interests=[
            UserInterestLinkRead(
                experience_level=link.experience_level,
                interest=InterestRead.model_validate(link.interest),
            )
            for link in profile.interest_links
        ],
        created_trips=[TripRead.model_validate(trip) for trip in profile.trips_created],
        joined_trips=[
            JoinedTripRead(
                participant_id=link.id or 0,
                status=link.status,
                note=link.note,
                contact_preference=link.contact_preference,
                trip=TripRead.model_validate(link.trip),
            )
            for link in profile.trip_links
        ],
    )


@app.get("/")
def hello():
    return "Hello, travel buddy finder with env and migrations!"


@app.get("/profiles", response_model=list[UserProfileRead])
def profiles_list(session: Session = Depends(get_session)):
    return session.exec(select(UserProfile)).all()


@app.get("/profile/{profile_id}", response_model=UserProfileDetails)
def profile_get(profile_id: int, session: Session = Depends(get_session)):
    statement = (
        select(UserProfile)
        .where(UserProfile.id == profile_id)
        .options(
            selectinload(cast(Any, UserProfile.interest_links)).selectinload(
                cast(Any, UserInterestLink.interest)
            ),
            selectinload(cast(Any, UserProfile.trips_created)),
            selectinload(cast(Any, UserProfile.trip_links)).selectinload(
                cast(Any, TripParticipantLink.trip)
            ),
        )
    )
    profile = session.exec(statement).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return serialize_profile_details(profile)


@app.post("/profile", response_model=UserProfileRead, status_code=201)
def profile_create(profile: UserProfileCreate, session: Session = Depends(get_session)):
    db_profile = UserProfile.model_validate(profile)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@app.patch("/profile/{profile_id}", response_model=UserProfileRead)
def profile_update(
    profile_id: int,
    profile: UserProfileUpdate,
    session: Session = Depends(get_session),
):
    db_profile = get_profile_or_404(session, profile_id)
    profile_data = profile.model_dump(exclude_unset=True)
    for key, value in profile_data.items():
        setattr(db_profile, key, value)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@app.delete("/profile/{profile_id}")
def profile_delete(profile_id: int, session: Session = Depends(get_session)):
    profile = get_profile_or_404(session, profile_id)
    session.delete(profile)
    session.commit()
    return {"ok": True}


@app.get("/interests", response_model=list[InterestRead])
def interests_list(session: Session = Depends(get_session)):
    return session.exec(select(Interest)).all()


@app.post("/interest", response_model=InterestRead, status_code=201)
def interest_create(interest: InterestCreate, session: Session = Depends(get_session)):
    db_interest = Interest.model_validate(interest)
    session.add(db_interest)
    session.commit()
    session.refresh(db_interest)
    return db_interest


@app.patch("/interest/{interest_id}", response_model=InterestRead)
def interest_update(
    interest_id: int,
    interest: InterestUpdate,
    session: Session = Depends(get_session),
):
    db_interest = get_interest_or_404(session, interest_id)
    interest_data = interest.model_dump(exclude_unset=True)
    for key, value in interest_data.items():
        setattr(db_interest, key, value)
    session.add(db_interest)
    session.commit()
    session.refresh(db_interest)
    return db_interest


@app.delete("/interest/{interest_id}")
def interest_delete(interest_id: int, session: Session = Depends(get_session)):
    interest = get_interest_or_404(session, interest_id)
    session.delete(interest)
    session.commit()
    return {"ok": True}


@app.post("/profile/{profile_id}/interest", response_model=UserProfileDetails)
def profile_add_interest(
    profile_id: int,
    link_data: UserInterestLinkCreate,
    session: Session = Depends(get_session),
):
    get_profile_or_404(session, profile_id)
    get_interest_or_404(session, link_data.interest_id)

    existing_link = session.get(UserInterestLink, (profile_id, link_data.interest_id))
    if existing_link:
        raise HTTPException(status_code=400, detail="Interest already added to profile")

    link = UserInterestLink(user_id=profile_id, **link_data.model_dump())
    session.add(link)
    session.commit()

    statement = (
        select(UserProfile)
        .where(UserProfile.id == profile_id)
        .options(
            selectinload(cast(Any, UserProfile.interest_links)).selectinload(
                cast(Any, UserInterestLink.interest)
            ),
            selectinload(cast(Any, UserProfile.trips_created)),
            selectinload(cast(Any, UserProfile.trip_links)).selectinload(
                cast(Any, TripParticipantLink.trip)
            ),
        )
    )
    profile = session.exec(statement).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return serialize_profile_details(profile)


@app.delete("/profile/{profile_id}/interest/{interest_id}")
def profile_remove_interest(
    profile_id: int,
    interest_id: int,
    session: Session = Depends(get_session),
):
    link = session.get(UserInterestLink, (profile_id, interest_id))
    if not link:
        raise HTTPException(status_code=404, detail="Interest link not found")
    session.delete(link)
    session.commit()
    return {"ok": True}


@app.get("/trips", response_model=list[TripRead])
def trips_list(session: Session = Depends(get_session)):
    return session.exec(select(Trip)).all()


@app.get("/trip/{trip_id}", response_model=TripDetails)
def trip_get(trip_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Trip)
        .where(Trip.id == trip_id)
        .options(
            selectinload(cast(Any, Trip.organizer)),
            selectinload(cast(Any, Trip.stops)),
            selectinload(cast(Any, Trip.participant_links)).selectinload(
                cast(Any, TripParticipantLink.traveler)
            ),
        )
    )
    trip = session.exec(statement).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return serialize_trip_details(trip)


@app.post("/trip", response_model=TripRead, status_code=201)
def trip_create(trip: TripCreate, session: Session = Depends(get_session)):
    get_profile_or_404(session, trip.organizer_id)
    db_trip = Trip.model_validate(trip)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip


@app.patch("/trip/{trip_id}", response_model=TripRead)
def trip_update(
    trip_id: int, trip: TripUpdate, session: Session = Depends(get_session)
):
    db_trip = get_trip_or_404(session, trip_id)
    trip_data = trip.model_dump(exclude_unset=True)

    if "organizer_id" in trip_data:
        get_profile_or_404(session, trip_data["organizer_id"])

    for key, value in trip_data.items():
        setattr(db_trip, key, value)
    session.add(db_trip)
    session.commit()
    session.refresh(db_trip)
    return db_trip


@app.delete("/trip/{trip_id}")
def trip_delete(trip_id: int, session: Session = Depends(get_session)):
    trip = get_trip_or_404(session, trip_id)
    session.delete(trip)
    session.commit()
    return {"ok": True}


@app.post("/trip/{trip_id}/stop", response_model=TripStopRead, status_code=201)
def trip_stop_create(
    trip_id: int,
    stop: TripStopCreate,
    session: Session = Depends(get_session),
):
    get_trip_or_404(session, trip_id)
    db_stop = TripStop(trip_id=trip_id, **stop.model_dump())
    session.add(db_stop)
    session.commit()
    session.refresh(db_stop)
    return db_stop


@app.patch("/trip-stop/{stop_id}", response_model=TripStopRead)
def trip_stop_update(
    stop_id: int,
    stop: TripStopUpdate,
    session: Session = Depends(get_session),
):
    db_stop = get_trip_stop_or_404(session, stop_id)
    stop_data = stop.model_dump(exclude_unset=True)
    for key, value in stop_data.items():
        setattr(db_stop, key, value)
    session.add(db_stop)
    session.commit()
    session.refresh(db_stop)
    return db_stop


@app.delete("/trip-stop/{stop_id}")
def trip_stop_delete(stop_id: int, session: Session = Depends(get_session)):
    stop = get_trip_stop_or_404(session, stop_id)
    session.delete(stop)
    session.commit()
    return {"ok": True}


@app.post(
    "/trip/{trip_id}/participant",
    response_model=TripParticipantLinkRead,
    status_code=201,
)
def trip_add_participant(
    trip_id: int,
    participant: TripParticipantLinkCreate,
    session: Session = Depends(get_session),
):
    get_trip_or_404(session, trip_id)
    get_profile_or_404(session, participant.traveler_id)

    existing_statement = select(TripParticipantLink).where(
        TripParticipantLink.trip_id == trip_id,
        TripParticipantLink.traveler_id == participant.traveler_id,
    )
    existing_link = session.exec(existing_statement).first()
    if existing_link:
        raise HTTPException(status_code=400, detail="Traveler already attached to trip")

    link = TripParticipantLink(trip_id=trip_id, **participant.model_dump())
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@app.patch("/trip-participant/{link_id}", response_model=TripParticipantLinkRead)
def trip_participant_update(
    link_id: int,
    participant: TripParticipantLinkUpdate,
    session: Session = Depends(get_session),
):
    db_link = get_participant_link_or_404(session, link_id)
    link_data = participant.model_dump(exclude_unset=True)
    for key, value in link_data.items():
        setattr(db_link, key, value)
    session.add(db_link)
    session.commit()
    session.refresh(db_link)
    return db_link


@app.delete("/trip-participant/{link_id}")
def trip_participant_delete(link_id: int, session: Session = Depends(get_session)):
    link = get_participant_link_or_404(session, link_id)
    session.delete(link)
    session.commit()
    return {"ok": True}
