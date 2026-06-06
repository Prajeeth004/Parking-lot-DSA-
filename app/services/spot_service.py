import heapq
from sqlalchemy.orm import Session
from app.models import ParkingSpot, SpotSize, VEHICLE_TO_SPOT, VehicleType

# ── Min-Heap (built once at startup) ─────────────────────────────────────────
_spot_heaps: dict[SpotSize, list[tuple[int, int, int]]] = {
    SpotSize.SMALL:  [],
    SpotSize.MEDIUM: [],
    SpotSize.LARGE:  [],
}

def build_heap(db: Session):
    """Called once at startup. Loads all free spots into heap."""
    spots = db.query(ParkingSpot).filter(ParkingSpot.is_occupied == False).all()
    for spot in spots:
        heapq.heappush(
            _spot_heaps[spot.spot_size],
            (spot.floor, spot.spot_number, spot.id)
        )

# ── REPLACED ──────────────────────────────────────────────────────────────────
def find_available_spot(db: Session, vehicle_type: VehicleType) -> ParkingSpot | None:
    """
    DSA: Min-Heap pop → nearest spot first.
    Time Complexity  : O(log n)
    Space Complexity : O(1) per call
    """
    required_size = VEHICLE_TO_SPOT[vehicle_type]
    heap = _spot_heaps[required_size]

    if not heap:
        return None  # lot full

    floor, spot_number, spot_id = heapq.heappop(heap)
    return db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).with_for_update().first()


# ── NO CHANGE ─────────────────────────────────────────────────────────────────
def assign_spot(db: Session, spot: ParkingSpot) -> ParkingSpot:
    spot.is_occupied = True
    db.commit()
    db.refresh(spot)
    return spot


# ── REPLACED ──────────────────────────────────────────────────────────────────
def free_spot(db: Session, spot: ParkingSpot) -> ParkingSpot:
    spot.is_occupied = False
    db.commit()
    db.refresh(spot)
    # push spot back into heap when vehicle exits
    heapq.heappush(
        _spot_heaps[spot.spot_size],
        (spot.floor, spot.spot_number, spot.id)
    )
    return spot


# ── NO CHANGE ─────────────────────────────────────────────────────────────────
def get_availability(db: Session, floor: int | None = None):
    """
    DSA: GROUP BY query → HashMap aggregation on SpotSize.
    Returns available vs occupied counts per spot type.
    """
    query = db.query(ParkingSpot)
    if floor is not None:
        query = query.filter(ParkingSpot.floor == floor)

    spots = query.all()

    summary: dict[SpotSize, dict] = {}

    for spot in spots:
        if spot.spot_size not in summary:
            summary[spot.spot_size] = {"total": 0, "available": 0, "occupied": 0}

        summary[spot.spot_size]["total"] += 1
        if spot.is_occupied:
            summary[spot.spot_size]["occupied"] += 1
        else:
            summary[spot.spot_size]["available"] += 1

    return summary