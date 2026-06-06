from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import EntryRequest, EntryResponse
from app.services import spot_service, ticket_service

router = APIRouter(prefix="/entry", tags=["Entry"])


@router.post("/", response_model=EntryResponse)
def vehicle_entry(payload: EntryRequest, db: Session = Depends(get_db)):

    # Edge case 1: vehicle already parked
    existing = ticket_service.get_ticket_by_vehicle(db, payload.vehicle_number)
    if existing:
        raise HTTPException(status_code=400, detail=f"Vehicle {payload.vehicle_number} is already parked. Ticket ID: {existing.id}")

    # Find nearest available spot (DSA: ordered linear search + row lock)
    spot = spot_service.find_available_spot(db, payload.vehicle_type)

    # Edge case 2: lot is full
    if not spot:
        raise HTTPException(status_code=404, detail=f"No available spot for {payload.vehicle_type}. Lot is full.")

    # Assign spot + generate ticket
    spot   = spot_service.assign_spot(db, spot)
    ticket = ticket_service.create_ticket(db, payload.vehicle_number, payload.vehicle_type, spot)

    return EntryResponse(
        ticket_id=ticket.id,
        vehicle_number=ticket.vehicle_number,
        vehicle_type=ticket.vehicle_type,
        spot_id=spot.id,
        floor=spot.floor,
        spot_number=spot.spot_number,
        entry_time=ticket.entry_time
    )