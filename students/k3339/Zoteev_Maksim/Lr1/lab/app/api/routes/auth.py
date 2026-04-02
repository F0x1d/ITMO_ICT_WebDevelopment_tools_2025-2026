from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth import (
    authenticate_user,
    build_token_response,
    get_user_by_email,
    get_user_by_username,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: RegisterRequest, session: SessionDep) -> UserRead:
    if get_user_by_email(session, payload.email):
        raise HTTPException(status_code=400, detail="Email is already registered")
    if get_user_by_username(session, payload.username):
        raise HTTPException(status_code=400, detail="Username is already taken")
    user = register_user(session, payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: SessionDep) -> TokenResponse:
    user = authenticate_user(session, payload)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return build_token_response(user)
