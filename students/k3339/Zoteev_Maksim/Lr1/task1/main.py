from fastapi import FastAPI, HTTPException

from models import Trip, TripCreate, UserProfile, UserProfileCreate

app = FastAPI(title="Travel Buddy Finder API")


profiles_db = [
    {
        "id": 1,
        "name": "Maksim Zoteev",
        "age": 20,
        "city": "Saint Petersburg",
        "bio": "Люблю бюджетные поездки, пешие маршруты и четкое планирование.",
        "travel_style": "budget",
        "languages": ["ru", "en"],
    },
    {
        "id": 2,
        "name": "Anna Smirnova",
        "age": 22,
        "city": "Moscow",
        "bio": "Предпочитаю спокойные путешествия, музеи и локальную кухню.",
        "travel_style": "relaxed",
        "languages": ["ru", "en", "it"],
    },
    {
        "id": 3,
        "name": "Ilya Petrov",
        "age": 24,
        "city": "Kazan",
        "bio": "Ищу попутчиков для активных маршрутов и поездок на машине.",
        "travel_style": "road_trip",
        "languages": ["ru"],
    },
]

trips_db = [
    {
        "id": 1,
        "title": "Выходные в Карелии",
        "departure_city": "Saint Petersburg",
        "destination_city": "Sortavala",
        "start_date": "2026-05-10",
        "end_date": "2026-05-12",
        "duration_days": 3,
        "description": "Поездка на выходные с прогулками по Рускеале и озерам.",
        "organizer": profiles_db[0],
        "stops": [
            {
                "id": 1,
                "location": "Priozersk",
                "days": 1,
                "note": "Короткая остановка по пути",
            },
            {
                "id": 2,
                "location": "Sortavala",
                "days": 2,
                "note": "Основная часть маршрута",
            },
        ],
    },
    {
        "id": 2,
        "title": "Казань и окрестности",
        "departure_city": "Moscow",
        "destination_city": "Kazan",
        "start_date": "2026-06-01",
        "end_date": "2026-06-05",
        "duration_days": 5,
        "description": "Городской тур с выездом в Свияжск и гастрономической программой.",
        "organizer": profiles_db[1],
        "stops": [
            {
                "id": 3,
                "location": "Kazan",
                "days": 4,
                "note": "Исторический центр и музеи",
            },
            {
                "id": 4,
                "location": "Sviyazhsk",
                "days": 1,
                "note": "Однодневная экскурсия",
            },
        ],
    },
]


@app.get("/")
def hello():
    return "Hello, travel buddy finder!"


@app.get("/profiles", response_model=list[UserProfile])
def get_profiles():
    return profiles_db


@app.get("/profile/{profile_id}", response_model=UserProfile)
def get_profile(profile_id: int):
    profile = next((item for item in profiles_db if item["id"] == profile_id), None)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@app.post("/profile", response_model=UserProfile, status_code=201)
def create_profile(profile: UserProfileCreate):
    new_profile = {"id": len(profiles_db) + 1, **profile.model_dump()}
    profiles_db.append(new_profile)
    return new_profile


@app.put("/profile/{profile_id}", response_model=UserProfile)
def update_profile(profile_id: int, profile: UserProfileCreate):
    for index, current_profile in enumerate(profiles_db):
        if current_profile["id"] == profile_id:
            updated_profile = {"id": profile_id, **profile.model_dump()}
            profiles_db[index] = updated_profile
            for trip in trips_db:
                if trip["organizer"]["id"] == profile_id:
                    trip["organizer"] = updated_profile
            return updated_profile
    raise HTTPException(status_code=404, detail="Profile not found")


@app.delete("/profile/{profile_id}")
def delete_profile(profile_id: int):
    for trip in trips_db:
        if trip["organizer"]["id"] == profile_id:
            raise HTTPException(status_code=400, detail="Profile is used in trips")

    for index, profile in enumerate(profiles_db):
        if profile["id"] == profile_id:
            profiles_db.pop(index)
            return {"status": 200, "message": "profile deleted"}
    raise HTTPException(status_code=404, detail="Profile not found")


@app.get("/trips", response_model=list[Trip])
def get_trips():
    return trips_db


@app.get("/trip/{trip_id}", response_model=Trip)
def get_trip(trip_id: int):
    trip = next((item for item in trips_db if item["id"] == trip_id), None)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@app.post("/trip", response_model=Trip, status_code=201)
def create_trip(trip: TripCreate):
    organizer = next(
        (item for item in profiles_db if item["id"] == trip.organizer_id), None
    )
    if organizer is None:
        raise HTTPException(status_code=404, detail="Organizer not found")

    next_stop_id = (
        max(
            (stop["id"] for trip_item in trips_db for stop in trip_item["stops"]),
            default=0,
        )
        + 1
    )
    new_stops = []
    for stop in trip.stops:
        new_stops.append({"id": next_stop_id, **stop.model_dump()})
        next_stop_id += 1

    new_trip = {
        "id": len(trips_db) + 1,
        "title": trip.title,
        "departure_city": trip.departure_city,
        "destination_city": trip.destination_city,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "duration_days": trip.duration_days,
        "description": trip.description,
        "organizer": organizer,
        "stops": new_stops,
    }
    trips_db.append(new_trip)
    return new_trip


@app.put("/trip/{trip_id}", response_model=Trip)
def update_trip(trip_id: int, trip: TripCreate):
    organizer = next(
        (item for item in profiles_db if item["id"] == trip.organizer_id), None
    )
    if organizer is None:
        raise HTTPException(status_code=404, detail="Organizer not found")

    for index, current_trip in enumerate(trips_db):
        if current_trip["id"] == trip_id:
            next_stop_id = (
                max(
                    (
                        stop["id"]
                        for trip_item in trips_db
                        for stop in trip_item["stops"]
                    ),
                    default=0,
                )
                + 1
            )
            updated_trip = {
                "id": trip_id,
                "title": trip.title,
                "departure_city": trip.departure_city,
                "destination_city": trip.destination_city,
                "start_date": trip.start_date,
                "end_date": trip.end_date,
                "duration_days": trip.duration_days,
                "description": trip.description,
                "organizer": organizer,
                "stops": [
                    {"id": next_stop_id + offset, **stop.model_dump()}
                    for offset, stop in enumerate(trip.stops)
                ],
            }
            trips_db[index] = updated_trip
            return updated_trip
    raise HTTPException(status_code=404, detail="Trip not found")


@app.delete("/trip/{trip_id}")
def delete_trip(trip_id: int):
    for index, trip in enumerate(trips_db):
        if trip["id"] == trip_id:
            trips_db.pop(index)
            return {"status": 200, "message": "trip deleted"}
    raise HTTPException(status_code=404, detail="Trip not found")
