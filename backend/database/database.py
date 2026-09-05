import os
import math
from typing import List, Tuple, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ner_yatri.db")

# Setup SQLAlchemy Engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL / PostGIS in Docker/Production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# Pure Python GIS / Geospatial Helpers
# (Ensures 100% portability across SQLite & PostGIS)
# ==========================================
from backend.routing.geo_utils import (
    haversine_distance,
    point_in_polygon,
    distance_point_to_linestring,
    interpolate_points
)

