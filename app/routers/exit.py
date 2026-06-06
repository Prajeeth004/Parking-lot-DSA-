from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ExitRequest, ExitResponse
from app.services import spot_service, ticket_service, fee_service

router = APIRouter(prefix="/exit", tags=["Exit"])


@router.post("/", response_model=ExitResponse)
def vehicle_exit(payload: ExitRequest, db: Session = Depends(get_db)):

    # Edge case 1: ticket not found or already closed
    ticket = ticket_service.get_active_ticket(db, payload.ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"No active ticket found with ID {payload.ticket_id}")

    # Calculate fee (DSA: HashMap lookup + ceil logic)
    from datetime import datetime
    exit_time = datetime.utcnow()
    duration_hours, fee = fee_service.calculate_fee(ticket.entry_time, exit_time, ticket.vehicle_type)

    # Free the spot
    spot_service.free_spot(db, ticket.spot)

    # Close ticket
    ticket = ticket_service.close_ticket(db, ticket, fee)

    return ExitResponse(
        ticket_id=ticket.id,
        vehicle_number=ticket.vehicle_number,
        vehicle_type=ticket.vehicle_type,
        entry_time=ticket.entry_time,
        exit_time=ticket.exit_time,
        duration_hours=duration_hours,
        fee=fee
    )