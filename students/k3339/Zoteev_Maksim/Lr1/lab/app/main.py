from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="Travel Partner Finder API")
app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Travel Partner Finder API"}
