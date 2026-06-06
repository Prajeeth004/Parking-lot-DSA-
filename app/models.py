from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class VehicleType(str, enum.Enum):
    BIKE  = "BIKE"
    CAR   = "CAR"
    TRUCK = "TRUCK"


class SpotSize(str, enum.Enum):
    SMALL  = "SMALL"   # Bike
    MEDIUM = "MEDIUM"  # Car
    LARGE  = "LARGE"   # Truck


# DSA: HashMap equivalent → vehicle_type maps to required spot size
VEHICLE_TO_SPOT: dict[VehicleType, SpotSize] = {
    VehicleType.BIKE:  SpotSize.SMALL,
    VehicleType.CAR:   SpotSize.MEDIUM,
    VehicleType.TRUCK: SpotSize.LARGE,
}

# Fee per hour for each vehicle type
HOURLY_RATE: dict[VehicleType, float] = {
    VehicleType.BIKE:  20.0,
    VehicleType.CAR:   50.0,
    VehicleType.TRUCK: 100.0,
}


class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id          = Column(Integer, primary_key=True, index=True)
    floor       = Column(Integer, nullable=False)          # Multi-floor support
    spot_number = Column(Integer, nullable=False)
    spot_size   = Column(Enum(SpotSize), nullable=False)
    is_occupied = Column(Boolean, default=False)

    tickets = relationship("Ticket", back_populates="spot")


class Ticket(Base):
    __tablename__ = "tickets"

    id           = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    spot_id      = Column(Integer, ForeignKey("parking_spots.id"))
    entry_time   = Column(DateTime, default=datetime.utcnow)
    exit_time    = Column(DateTime, nullable=True)
    fee          = Column(Float, nullable=True)
    is_active    = Column(Boolean, default=True)

    spot = relationship("ParkingSpot", back_populates="tickets")