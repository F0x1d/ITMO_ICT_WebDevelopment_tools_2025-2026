import os

from dotenv import load_dotenv
from sqlmodel import Session, create_engine


load_dotenv()

DATABASE_URL = os.getenv(
    "DB_ADMIN",
    "postgresql://postgres:123@localhost/travel_buddy_db",
)

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
