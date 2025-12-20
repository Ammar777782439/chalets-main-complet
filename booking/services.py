from datetime import datetime, time, timedelta
from django.db.models import Q
from django.utils import timezone
from .models import Booking


def is_timeslot_available(*, property_obj, start_dt, end_dt, exclude_booking_id=None):
    """
    Returns True if the timeslot [start_dt, end_dt) is available for the given property.
    Considers bookings with status in ['pending','confirmed'].
    Treats legacy date-only bookings as full-day blocks on their booking_date.
    """
    if start_dt >= end_dt:
        return False

    qs = Booking.objects.filter(status__in=['pending', 'confirmed'])
    qs = qs.filter(property=property_obj)

    if exclude_booking_id:
        qs = qs.exclude(id=exclude_booking_id)

    # Overlap for timeslot-based bookings (both start and end must exist)
    overlap_q = Q(
        start_datetime__isnull=False,
        end_datetime__isnull=False,
        start_datetime__lt=end_dt,
        end_datetime__gt=start_dt
    )

    # Legacy date-only bookings: treat as whole day of booking_date
    if isinstance(start_dt, datetime):
        start_day = start_dt.date()
        end_day = end_dt.date()
    else:
        start_day = end_day = None

    legacy_q = Q(start_datetime__isnull=True, end_datetime__isnull=True) & (
        Q(booking_date=start_day) | Q(booking_date=end_day)
    )

    conflicting_bookings = qs.filter(overlap_q | legacy_q)
    
    return not conflicting_bookings.exists()
