from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models import Trip, TripParticipantLink, TripStop
from app.schemas.trip import (
    TripCreate,
    TripDetails,
    TripParticipantCreate,
    TripParticipantRead,
    TripParticipantUpdate,
    TripShortRead,
    TripStopCreate,
    TripStopRead,
    TripStopUpdate,
    TripUpdate,
)
from app.services.serializers import get_trip_with_details, serialize_trip_details

router = APIRouter(prefix="/trips", tags=["trips"])


def get_trip_or_404(session: SessionDep, trip_id: int) -> Trip:
    trip = session.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def get_stop_or_404(session: SessionDep, stop_id: int) -> TripStop:
    stop = session.get(TripStop, stop_id)
    if stop is None:
        raise HTTPException(status_code=404, detail="Trip stop not found")
    return stop


def get_participant_or_404(
    session: SessionDep, participant_id: int
) -> TripParticipantLink:
    participant = session.get(TripParticipantLink, participant_id)
    if participant is None:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant


@router.get("", response_model=list[TripShortRead])
def list_trips(session: SessionDep) -> list[TripShortRead]:
    trips = session.exec(select(Trip)).all()
    return [TripShortRead.model_validate(trip) for trip in trips]


@router.get("/{trip_id}", response_model=TripDetails)
def get_trip(trip_id: int, session: SessionDep) -> TripDetails:
    trip = get_trip_with_details(session, trip_id)
    return serialize_trip_details(trip)


@router.post("", response_model=TripShortRead, status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TripShortRead:
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="Current user id is missing")

    trip = Trip(organizer_id=current_user.id, **payload.model_dump())
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return TripShortRead.model_validate(trip)


@router.patch("/{trip_id}", response_model=TripShortRead)
def update_trip(
    trip_id: int,
    payload: TripUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TripShortRead:
    trip = get_trip_or_404(session, trip_id)
    if trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can update trip")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(trip, key, value)

    session.add(trip)
    session.commit()
    session.refresh(trip)
    return TripShortRead.model_validate(trip)


@router.delete("/{trip_id}")
def delete_trip(
    trip_id: int,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, bool]:
    trip = get_trip_or_404(session, trip_id)
    if trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can delete trip")
    session.delete(trip)
    session.commit()
    return {"ok": True}


@router.post("/{trip_id}/stops", response_model=TripStopRead, status_code=201)
def create_trip_stop(
    trip_id: int,
    payload: TripStopCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TripStopRead:
    trip = get_trip_or_404(session, trip_id)
    if trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can add stops")

    stop = TripStop(trip_id=trip_id, **payload.model_dump())
    session.add(stop)
    session.commit()
    session.refresh(stop)
    return TripStopRead.model_validate(stop)


@router.patch("/stops/{stop_id}", response_model=TripStopRead)
def update_trip_stop(
    stop_id: int,
    payload: TripStopUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TripStopRead:
    stop = get_stop_or_404(session, stop_id)
    trip = get_trip_or_404(session, stop.trip_id)
    if trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can update stops")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(stop, key, value)

    session.add(stop)
    session.commit()
    session.refresh(stop)
    return TripStopRead.model_validate(stop)


@router.delete("/stops/{stop_id}")
def delete_trip_stop(
    stop_id: int,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, bool]:
    stop = get_stop_or_404(session, stop_id)
    trip = get_trip_or_404(session, stop.trip_id)
    if trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only organizer can delete stops")
    session.delete(stop)
    session.commit()
    return {"ok": True}


@router.post(
    "/{trip_id}/participants", response_model=TripParticipantRead, status_code=201
)
def add_trip_participant(
    trip_id: int,
    payload: TripParticipantCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TripParticipantRead:
    trip = get_trip_or_404(session, trip_id)
    if payload.user_id != current_user.id and trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot add another participant")

    statement = select(TripParticipantLink).where(
        TripParticipantLink.trip_id == trip_id,
        TripParticipantLink.user_id == payload.user_id,
    )
    if session.exec(statement).first() is not None:
        raise HTTPException(status_code=400, detail="Participant already exists")

    participant = TripParticipantLink(trip_id=trip_id, **payload.model_dump())
    session.add(participant)
    session.commit()
    session.refresh(participant)
    return TripParticipantRead.model_validate(participant)


@router.patch("/participants/{participant_id}", response_model=TripParticipantRead)
def update_trip_participant(
    participant_id: int,
    payload: TripParticipantUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> TripParticipantRead:
    participant = get_participant_or_404(session, participant_id)
    trip = get_trip_or_404(session, participant.trip_id)
    if participant.user_id != current_user.id and trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot update this participant")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(participant, key, value)

    session.add(participant)
    session.commit()
    session.refresh(participant)
    return TripParticipantRead.model_validate(participant)


@router.delete("/participants/{participant_id}")
def delete_trip_participant(
    participant_id: int,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, bool]:
    participant = get_participant_or_404(session, participant_id)
    trip = get_trip_or_404(session, participant.trip_id)
    if participant.user_id != current_user.id and trip.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete this participant")
    session.delete(participant)
    session.commit()
    return {"ok": True}
