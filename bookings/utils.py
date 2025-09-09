from datetime import datetime
from .models import Table, Booking

def available_tables(date, time, guests, exclude_booking=None):
    if isinstance(date, str):
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return None
    else:
        date_obj = date
    
    if isinstance(time, str):
        try:
            time_obj = datetime.strptime(time, '%H:%M').time()
        except ValueError:
            return None
    else:
        time_obj = time

    # Get all tables that are already booked for this date and time
    bookings_query = Booking.objects.filter(date=date_obj, time=time_obj)
    
    # Exclude current booking if editing
    if exclude_booking:
        bookings_query = bookings_query.exclude(id=exclude_booking.id)
    
    booked_table_ids = bookings_query.values_list('tables__id', flat=True).distinct()

    # Get available tables
    available = Table.objects.exclude(id__in=booked_table_ids).order_by('seats')

    # Find combination of tables that can accommodate guests
    seats_needed = guests
    tables_allocated = []
    
    for table in available:
        if seats_needed <= 0:
            break
        tables_allocated.append(table)
        seats_needed -= table.seats
    
    return tables_allocated if seats_needed <= 0 else None