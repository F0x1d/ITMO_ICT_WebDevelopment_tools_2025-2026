from pydantic import BaseModel, Field, field_validator

from app.models.enums import TravelStyle


class RegisterRequest(BaseModel):
    email: str
    username: str
    full_name: str
    age: int
    city: str
    bio: str | None = None
    travel_style: TravelStyle
    telegram_username: str | None = None
    languages: list[str] = Field(default_factory=list)
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("current_password", "new_password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long")
        return value
