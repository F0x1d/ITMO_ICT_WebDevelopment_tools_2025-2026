from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InterestCreate(BaseModel):
    name: str
    description: str


class InterestUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class InterestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class UserInterestCreate(BaseModel):
    interest_id: int
    experience_level: str = "beginner"


class UserInterestUpdate(BaseModel):
    experience_level: str


class UserInterestRead(BaseModel):
    interest: InterestRead
    experience_level: str
