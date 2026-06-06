from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AvailabilityResponse, SpotAvailability
from app.services import spot_service
from typing import Optional

router = APIRouter(prefix="/availability", tags=["Availability"])


@router.get("/", response_model=AvailabilityResponse)
def get_availability(
    floor: Optional[int] = Query(default=None, description="Filter by floor number"),
    db: Session = Depends(get_db)
):
    """
    Returns available vs occupied spots per type.
    Optionally filter by floor.

    DSA: HashMap aggregation → O(n) scan, O(k) space where k = spot types
    """
    summary = spot_service.get_availability(db, floor)

    availability = [
        SpotAvailability(
            spot_size=size,
            total=data["total"],
            available=data["available"],
            occupied=data["occupied"]
        )
        for size, data in summary.items()
    ]

    return AvailabilityResponse(floor=floor, availability=availability)