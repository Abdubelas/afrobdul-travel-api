from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time

app = FastAPI(title="Afrobdul Travel API", version="1.0.0",
              description="🌍 Tracking every trip, one endpoint at a time.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel.db")

Base = declarative_base()

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String)
    city = Column(String)
    year = Column(Integer)
    rating = Column(Float)
    notes = Column(String)

def get_engine():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()
            return engine
        except Exception:
            retries -= 1
            print(f"Database not ready, retrying... ({retries} left)")
            time.sleep(3)
    raise Exception("Could not connect to database")

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    if db.query(Trip).count() == 0:
        trips = [
            Trip(country="Japan", city="Tokyo", year=2022, rating=5, notes="First time in Japan, absolute must visit"),
            Trip(country="Japan", city="Kyoto", year=2022, rating=5, notes="Most peaceful city ever"),
            Trip(country="Japan", city="Tokyo", year=2024, rating=5, notes="Second time, just as good"),
            Trip(country="Japan", city="Kyoto", year=2024, rating=5, notes="Back again, never gets old"),
            Trip(country="Japan", city="Fukuoka", year=2024, rating=5, notes="Hidden gem, incredible food scene"),
            Trip(country="United Kingdom", city="Liverpool", year=2025, rating=5, notes="Liverpool vs PSG Champions League Leg 2"),
            Trip(country="United Kingdom", city="London", year=2025, rating=5, notes="Classic London visit"),
            Trip(country="United States", city="Seattle", year=2025, rating=4, notes="Lake 22 hike, stunning views"),
            Trip(country="Canada", city="Banff", year=2025, rating=5, notes="Banff National Park and Lake Louise, unreal scenery"),
            Trip(country="United States", city="Zion", year=2025, rating=5, notes="The Narrows hike in Zion National Park"),
            Trip(country="United States", city="Jackson", year=2025, rating=5, notes="Grand Tetons, breathtaking mountains"),
            Trip(country="United States", city="Portland", year=2025, rating=4, notes="Mount Hood and Cannon Beach"),
            Trip(country="United States", city="Anchorage", year=2025, rating=5, notes="Alaska hikes, wild and untouched"),
            Trip(country="France", city="Paris", year=2025, rating=4, notes="Classic Paris trip"),
            Trip(country="Morocco", city="Marrakech", year=2026, rating=5, notes="AFCON, incredible atmosphere"),
            Trip(country="Portugal", city="Madeira", year=2026, rating=5, notes="Madeira island, hidden paradise"),
        ]
        db.add_all(trips)
        db.commit()
    db.close()

seed_data()

@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse("/app/dashboard.html")

@app.get("/")
def root():
    return {"message": "Welcome to the Afrobdul Travel API 🌍"}

@app.get("/trips")
def get_all_trips():
    db = SessionLocal()
    trips = db.query(Trip).all()
    db.close()
    return {"total": len(trips), "trips": trips}

@app.get("/trips/{trip_id}")
def get_trip(trip_id: int):
    db = SessionLocal()
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    db.close()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.get("/stats")
def get_stats():
    db = SessionLocal()
    trips = db.query(Trip).all()
    db.close()
    countries = list(set([t.country for t in trips]))
    return {
        "total_trips": len(trips),
        "countries_visited": len(countries),
        "countries": countries,
        "average_rating": sum([t.rating for t in trips]) / len(trips)
    }