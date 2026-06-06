from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Ticket, ParkingSpot, VehicleType


def create_ticket(db: Session, vehicle_number: str, vehicle_type: VehicleType, spot: ParkingSpot) -> Ticket:
    ticket = Ticket(
        vehicle_number=vehicle_number,
        vehicle_type=vehicle_type,
        spot_id=spot.id,
        entry_time=datetime.utcnow(),
        is_active=True
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_active_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.is_active == True
    ).first()


def close_ticket(db: Session, ticket: Ticket, fee: float) -> Ticket:
    ticket.exit_time = datetime.utcnow()
    ticket.fee       = fee
    ticket.is_active = False
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket_by_vehicle(db: Session, vehicle_number: str) -> Ticket | None:
    """Edge case check: prevent same vehicle entering twice."""
    return db.query(Ticket).filter(
        Ticket.vehicle_number == vehicle_number,
        Ticket.is_active == True
    ).first()