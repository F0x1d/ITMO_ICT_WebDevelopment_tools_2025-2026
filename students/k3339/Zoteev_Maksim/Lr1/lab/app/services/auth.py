from sqlmodel import Session, select

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def register_user(session: Session, payload: RegisterRequest) -> User:
    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        age=payload.age,
        city=payload.city,
        bio=payload.bio,
        travel_style=payload.travel_style,
        telegram_username=payload.telegram_username,
        languages=payload.languages,
        password_hash=get_password_hash(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, payload: LoginRequest) -> User | None:
    user = get_user_by_email(session, payload.email)
    if not user:
        return None
    if not verify_password(payload.password, user.password_hash):
        return None
    return user


def build_token_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(str(user.id)))
