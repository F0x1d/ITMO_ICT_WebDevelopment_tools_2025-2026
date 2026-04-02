from datetime import date

from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.db.session import engine
from app.models import (
    Interest,
    Trip,
    TripParticipantLink,
    TripStop,
    User,
    UserInterestLink,
)
from app.models.enums import ParticipantStatus, TravelStyle


def get_or_create_user(session: Session, **kwargs) -> User:
    existing = session.exec(select(User).where(User.email == kwargs["email"])).first()
    if existing:
        return existing

    user = User(**kwargs)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_or_create_interest(session: Session, **kwargs) -> Interest:
    existing = session.exec(
        select(Interest).where(Interest.name == kwargs["name"])
    ).first()
    if existing:
        return existing

    interest = Interest(**kwargs)
    session.add(interest)
    session.commit()
    session.refresh(interest)
    return interest


def get_or_create_trip(session: Session, **kwargs) -> Trip:
    existing = session.exec(
        select(Trip).where(
            Trip.title == kwargs["title"],
            Trip.organizer_id == kwargs["organizer_id"],
        )
    ).first()
    if existing:
        return existing

    trip = Trip(**kwargs)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip


def add_user_interest(
    session: Session, user_id: int, interest_id: int, experience_level: str
) -> None:
    existing = session.get(UserInterestLink, (user_id, interest_id))
    if existing:
        return

    link = UserInterestLink(
        user_id=user_id,
        interest_id=interest_id,
        experience_level=experience_level,
    )
    session.add(link)
    session.commit()


def add_trip_stop(
    session: Session, trip_id: int, location: str, days: int, note: str
) -> None:
    existing = session.exec(
        select(TripStop).where(
            TripStop.trip_id == trip_id,
            TripStop.location == location,
        )
    ).first()
    if existing:
        return

    stop = TripStop(trip_id=trip_id, location=location, days=days, note=note)
    session.add(stop)
    session.commit()


def add_trip_participant(
    session: Session,
    trip_id: int,
    user_id: int,
    status: ParticipantStatus,
    message: str,
    contact_preference: str,
) -> None:
    existing = session.exec(
        select(TripParticipantLink).where(
            TripParticipantLink.trip_id == trip_id,
            TripParticipantLink.user_id == user_id,
        )
    ).first()
    if existing:
        return

    participant = TripParticipantLink(
        trip_id=trip_id,
        user_id=user_id,
        status=status,
        message=message,
        contact_preference=contact_preference,
    )
    session.add(participant)
    session.commit()


def main() -> None:
    with Session(engine) as session:
        maxim = get_or_create_user(
            session,
            email="maxim@example.com",
            username="maxim_z",
            full_name="Maksim Zoteev",
            age=20,
            city="Saint Petersburg",
            bio="Люблю бюджетные поездки и четко планировать маршрут.",
            travel_style=TravelStyle.budget,
            telegram_username="@maxim_trip",
            languages=["ru", "en"],
            password_hash=get_password_hash("12345678"),
        )

        anna = get_or_create_user(
            session,
            email="anna@example.com",
            username="anna_s",
            full_name="Anna Smirnova",
            age=22,
            city="Moscow",
            bio="Ищу спокойные поездки, музеи и красивую архитектуру.",
            travel_style=TravelStyle.relaxed,
            telegram_username="@anna_go",
            languages=["ru", "en", "it"],
            password_hash=get_password_hash("12345678"),
        )

        ilya = get_or_create_user(
            session,
            email="ilya@example.com",
            username="ilya_drive",
            full_name="Ilya Petrov",
            age=24,
            city="Kazan",
            bio="Люблю road trip, природу и активные маршруты.",
            travel_style=TravelStyle.road_trip,
            telegram_username="@ilya_road",
            languages=["ru"],
            password_hash=get_password_hash("12345678"),
        )

        hiking = get_or_create_interest(
            session,
            name="Пешие маршруты",
            description="Хайкинг, треккинг и прогулки по природным маршрутам.",
        )
        museums = get_or_create_interest(
            session,
            name="Музеи",
            description="Посещение музеев, исторических мест и выставок.",
        )
        road_trips = get_or_create_interest(
            session,
            name="Road trips",
            description="Путешествия на машине по нескольким городам и локациям.",
        )

        add_user_interest(session, maxim.id, hiking.id, "advanced")
        add_user_interest(session, anna.id, museums.id, "intermediate")
        add_user_interest(session, ilya.id, road_trips.id, "advanced")
        add_user_interest(session, ilya.id, hiking.id, "intermediate")

        karelia_trip = get_or_create_trip(
            session,
            title="Выходные в Карелии",
            departure_city="Saint Petersburg",
            destination_city="Sortavala",
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 12),
            duration_days=3,
            description="Поездка на выходные с прогулками по Рускеале и озерам.",
            organizer_id=maxim.id,
        )

        kazan_trip = get_or_create_trip(
            session,
            title="Казань и окрестности",
            departure_city="Moscow",
            destination_city="Kazan",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 5),
            duration_days=5,
            description="Городской тур с выездом в Свияжск и гастрономической программой.",
            organizer_id=anna.id,
        )

        add_trip_stop(
            session,
            karelia_trip.id,
            "Priozersk",
            1,
            "Короткая остановка по пути.",
        )
        add_trip_stop(
            session,
            karelia_trip.id,
            "Sortavala",
            2,
            "Основная часть маршрута и прогулки по Рускеале.",
        )
        add_trip_stop(
            session,
            kazan_trip.id,
            "Kazan",
            4,
            "Исторический центр, кремль и музеи.",
        )
        add_trip_stop(
            session,
            kazan_trip.id,
            "Sviyazhsk",
            1,
            "Однодневная экскурсия в остров-град.",
        )

        add_trip_participant(
            session,
            karelia_trip.id,
            anna.id,
            ParticipantStatus.approved,
            "Хочу поехать ради природы и фотографий.",
            "telegram",
        )
        add_trip_participant(
            session,
            kazan_trip.id,
            ilya.id,
            ParticipantStatus.pending,
            "Интересен маршрут и поездка по окрестностям.",
            "telegram",
        )

    print("Seed data inserted successfully.")


if __name__ == "__main__":
    main()
