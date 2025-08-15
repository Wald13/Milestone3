from django.shortcuts import render
from .models import Table, Booking



def available_tables(date, time, guests):
    # Find tables already booked at the given date/time
    booked_tables = Booking.objects.filter(
        date=date,
        time=time
    ).values_list('tables', flat=True)

    # Get available tables sorted by seat count
    available = Table.objects.exclude(id__in=booked_tables).order_by('seats')

    seats_needed = guests
    tables_allocated = []

    for table in available:
        tables_allocated.append(table)
        seats_needed -= table.seats
        if seats_needed <= 0:
            return tables_allocated  # Enough tables found
    
    return None  # Not enough tables