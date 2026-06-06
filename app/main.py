from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, SessionLocal
from app.models import Base, ParkingSpot, SpotSize
from app.routers import entry, exit, availability
from app.services.spot_service import build_heap  # added

app = FastAPI(title="Parking Lot System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(entry.router)
app.include_router(exit.router)
app.include_router(availability.router)


# ── DB Init + Seed ────────────────────────────────────────────────────────────
def seed_parking_spots():
    """
    Seed the lot with spots across 3 floors.

    Floor layout per floor:
        SMALL  spots (Bike)  : 5
        MEDIUM spots (Car)   : 5
        LARGE  spots (Truck) : 2
    """
    db = SessionLocal()
    if db.query(ParkingSpot).count() > 0:
        db.close()
        return  # already seeded

    spots = []
    for floor in range(1, 4):          # 3 floors
        spot_number = 1

        for _ in range(5):             # 5 bike spots
            spots.append(ParkingSpot(floor=floor, spot_number=spot_number, spot_size=SpotSize.SMALL))
            spot_number += 1

        for _ in range(5):             # 5 car spots
            spots.append(ParkingSpot(floor=floor, spot_number=spot_number, spot_size=SpotSize.MEDIUM))
            spot_number += 1

        for _ in range(2):             # 2 truck spots
            spots.append(ParkingSpot(floor=floor, spot_number=spot_number, spot_size=SpotSize.LARGE))
            spot_number += 1

    db.add_all(spots)
    db.commit()
    db.close()
    print(f"[SUCCESS] Seeded {len(spots)} parking spots across 3 floors.")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    seed_parking_spots()

    db = SessionLocal()
    build_heap(db)    # added — loads free spots into heap after seeding
    db.close()


@app.get("/")
def root():
    return {
        "message": "Parking Lot API",
        "docs": "/docs",
        "floors": 3,
        "spot_types": ["SMALL (Bike)", "MEDIUM (Car)", "LARGE (Truck)"]
    }