import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from backend.database.database import engine, Base
from database.seed.seed_data import seed_all_demo_data

# Import route modules
from backend.routes.auth import router as auth_router
from backend.routes.risk import router as risk_router
from backend.routes.weather import router as weather_router
from backend.routes.roads import router as roads_router
from backend.routes.reports import router as reports_router
from backend.routes.routes_optimizer import router as routing_router
from backend.routes.alerts import router as alerts_router
from backend.routes.satellite import router as satellite_router
from backend.routes.simulation import router as simulation_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.system import router as system_router
from backend.routes.audit import router as audit_router

load_dotenv()

ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174"
    ).split(",") if origin.strip()
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and seed demo data if empty
    Base.metadata.create_all(bind=engine)
    try:
        seed_all_demo_data()
    except Exception as e:
        print(f"Seed initialization notice: {e}")
    yield
    # Shutdown logic if needed


app = FastAPI(
    title="NER YATRI API",
    description="AI-Based Smart Logistics & Accessibility Intelligence Platform for North Eastern Region",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists and mount static files
os.makedirs("backend/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")

# Register API Routers
app.include_router(auth_router)
app.include_router(risk_router)
app.include_router(weather_router)
app.include_router(roads_router)
app.include_router(reports_router)
app.include_router(routing_router)
app.include_router(alerts_router)
app.include_router(satellite_router)
app.include_router(simulation_router)
app.include_router(dashboard_router)
app.include_router(system_router)
app.include_router(audit_router)


@app.get("/")
def root():
    return {
        "system": "NER YATRI API",
        "region": "North Eastern Region of India (Assam, Arunachal, Meghalaya, Manipur, Mizoram, Nagaland, Tripura, Sikkim)",
        "version": "1.0.0",
        "status": "ONLINE",
        "docs": "/api/docs",
        "disclaimer": "Predicted risk for 6–24 hours. Demonstrator system."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
