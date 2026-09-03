from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import engine
from app.routers import searches, stations, trips
from app.routers import predictions

app = FastAPI(
    title="Smart Mobility API",
    description="Backend API for the Smart Mobility Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stations.router)
app.include_router(trips.router)
app.include_router(searches.router)
app.include_router(predictions.router)


@app.get("/")
def root():
    return {
        "application": "Smart Mobility",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health/database")
def database_health():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database()")
        )

        database_name = result.scalar()

    return {
        "database": database_name,
        "status": "connected",
    }