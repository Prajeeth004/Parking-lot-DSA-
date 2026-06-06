from datetime import datetime
from math import ceil
from app.models import VehicleType, HOURLY_RATE


def calculate_fee(entry_time: datetime, exit_time: datetime, vehicle_type: VehicleType) -> tuple[float, float]:
    """
    Fee Calculation Logic
    ─────────────────────
    duration = exit_time - entry_time  (in hours)
    fee      = ceil(duration) * hourly_rate[vehicle_type]

    DSA: HashMap lookup → O(1) rate fetch
    
    ceil() ensures partial hours are billed as full hours.
    Example:
        entry = 10:00, exit = 11:45 → duration = 1.75 hrs → ceil = 2 hrs
        vehicle = CAR  → rate = 50/hr
        fee = 2 * 50 = ₹100

    Args:
        entry_time   : datetime when vehicle entered
        exit_time    : datetime when vehicle exited
        vehicle_type : BIKE / CAR / TRUCK

    Returns:
        (duration_hours, fee)
    """
    delta          = exit_time - entry_time
    duration_hours = delta.total_seconds() / 3600          # exact float hours
    billed_hours   = ceil(duration_hours) if duration_hours > 0 else 1   # min 1 hour

    rate = HOURLY_RATE[vehicle_type]                        # O(1) HashMap lookup
    fee  = billed_hours * rate

    return round(duration_hours, 2), round(fee, 2)