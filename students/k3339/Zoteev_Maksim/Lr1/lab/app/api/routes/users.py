from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep
from app.core.security import get_password_hash, verify_password
from app.models import User, UserInterestLink
from app.schemas.auth import ChangePasswordRequest
from app.schemas.interest import UserInterestCreate, UserInterestUpdate
from app.schemas.user import UserDetails, UserRead, UserUpdate
from app.services.auth import get_user_by_username
from app.services.serializers import get_user_with_details, serialize_user_details

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(session: SessionDep) -> list[UserRead]:
    users = session.exec(select(User)).all()
    return [UserRead.model_validate(user) for user in users]


@router.get("/me", response_model=UserDetails)
def get_me(current_user: CurrentUserDep, session: SessionDep) -> UserDetails:
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="Current user id is missing")
    user = get_user_with_details(session, current_user.id)
    return serialize_user_details(user)


@router.get("/{user_id}", response_model=UserDetails)
def get_user(user_id: int, session: SessionDep) -> UserDetails:
    user = get_user_with_details(session, user_id)
    return serialize_user_details(user)


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> UserRead:
    data = payload.model_dump(exclude_unset=True)

    if "username" in data and data["username"] != current_user.username:
        if get_user_by_username(session, data["username"]):
            raise HTTPException(status_code=400, detail="Username is already taken")

    for key, value in data.items():
        setattr(current_user, key, value)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return UserRead.model_validate(current_user)


@router.post("/me/change-password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, bool]:
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    current_user.password_hash = get_password_hash(payload.new_password)
    session.add(current_user)
    session.commit()
    return {"ok": True}


@router.delete("/me")
def delete_me(current_user: CurrentUserDep, session: SessionDep) -> dict[str, bool]:
    session.delete(current_user)
    session.commit()
    return {"ok": True}


@router.post("/me/interests", response_model=UserDetails)
def add_interest_to_me(
    payload: UserInterestCreate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> UserDetails:
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="Current user id is missing")

    existing = session.get(UserInterestLink, (current_user.id, payload.interest_id))
    if existing:
        raise HTTPException(status_code=400, detail="Interest already added")

    link = UserInterestLink(
        user_id=current_user.id,
        interest_id=payload.interest_id,
        experience_level=payload.experience_level,
    )
    session.add(link)
    session.commit()
    user = get_user_with_details(session, current_user.id)
    return serialize_user_details(user)


@router.patch("/me/interests/{interest_id}", response_model=UserDetails)
def update_my_interest(
    interest_id: int,
    payload: UserInterestUpdate,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> UserDetails:
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="Current user id is missing")

    link = session.get(UserInterestLink, (current_user.id, interest_id))
    if link is None:
        raise HTTPException(status_code=404, detail="Interest link not found")

    link.experience_level = payload.experience_level
    session.add(link)
    session.commit()
    user = get_user_with_details(session, current_user.id)
    return serialize_user_details(user)


@router.delete("/me/interests/{interest_id}")
def delete_my_interest(
    interest_id: int,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict[str, bool]:
    if current_user.id is None:
        raise HTTPException(status_code=500, detail="Current user id is missing")

    link = session.get(UserInterestLink, (current_user.id, interest_id))
    if link is None:
        raise HTTPException(status_code=404, detail="Interest link not found")
    session.delete(link)
    session.commit()
    return {"ok": True}
