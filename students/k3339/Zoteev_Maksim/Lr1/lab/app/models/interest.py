from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class InterestBase(SQLModel):
    name: str
    description: str


class Interest(InterestBase, table=True):
    __tablename__ = "interests"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)

    user_links: list["UserInterestLink"] = Relationship(
        back_populates="interest",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class UserInterestLink(SQLModel, table=True):
    __tablename__ = "user_interests"  # type: ignore[assignment]

    user_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        primary_key=True,
    )
    interest_id: Optional[int] = Field(
        default=None,
        foreign_key="interests.id",
        primary_key=True,
    )
    experience_level: str = Field(default="beginner")

    user: Optional["User"] = Relationship(back_populates="interest_links")
    interest: Optional["Interest"] = Relationship(back_populates="user_links")
