from pydantic import BaseModel
from datetime import datetime
from app.models import VehicleType, SpotSize
from typing import Optional


class EntryRequest(BaseModel):
    vehicle_number: str
    vehicle_type: VehicleType


class EntryResponse(BaseModel):
    ticket_id: int
    vehicle_number: str
    vehicle_type: VehicleType
    spot_id: int
    floor: int
    spot_number: int
    entry_time: datetime

    class Config:
        from_attributes = True


class ExitRequest(BaseModel):
    ticket_id: int


class ExitResponse(BaseModel):
    ticket_id: int
    vehicle_number: str
    vehicle_type: VehicleType
    entry_time: datetime
    exit_time: datetime
    duration_hours: float
    fee: float

    class Config:
        from_attributes = True


class SpotAvailability(BaseModel):
    spot_size: SpotSize
    total: int
    available: int
    occupied: int


class AvailabilityResponse(BaseModel):
    floor: Optional[int] = None
    availability: list[SpotAvailability]