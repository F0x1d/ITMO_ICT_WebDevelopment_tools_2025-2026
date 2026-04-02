from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models import Interest
from app.schemas.interest import InterestCreate, InterestRead, InterestUpdate

router = APIRouter(prefix="/interests", tags=["interests"])


@router.get("", response_model=list[InterestRead])
def list_interests(session: SessionDep) -> list[InterestRead]:
    interests = session.exec(select(Interest)).all()
    return [InterestRead.model_validate(interest) for interest in interests]


@router.get("/{interest_id}", response_model=InterestRead)
def get_interest(interest_id: int, session: SessionDep) -> InterestRead:
    interest = session.get(Interest, interest_id)
    if interest is None:
        raise HTTPException(status_code=404, detail="Interest not found")
    return InterestRead.model_validate(interest)


@router.post("", response_model=InterestRead, status_code=status.HTTP_201_CREATED)
def create_interest(
    payload: InterestCreate,
    _: CurrentUserDep,
    session: SessionDep,
) -> InterestRead:
    interest = Interest.model_validate(payload)
    session.add(interest)
    session.commit()
    session.refresh(interest)
    return InterestRead.model_validate(interest)


@router.patch("/{interest_id}", response_model=InterestRead)
def update_interest(
    interest_id: int,
    payload: InterestUpdate,
    _: CurrentUserDep,
    session: SessionDep,
) -> InterestRead:
    interest = session.get(Interest, interest_id)
    if interest is None:
        raise HTTPException(status_code=404, detail="Interest not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(interest, key, value)

    session.add(interest)
    session.commit()
    session.refresh(interest)
    return InterestRead.model_validate(interest)


@router.delete("/{interest_id}")
def delete_interest(
    interest_id: int,
    _: CurrentUserDep,
    session: SessionDep,
) -> dict[str, bool]:
    interest = session.get(Interest, interest_id)
    if interest is None:
        raise HTTPException(status_code=404, detail="Interest not found")
    session.delete(interest)
    session.commit()
    return {"ok": True}
