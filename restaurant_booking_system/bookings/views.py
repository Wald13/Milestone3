from django.shortcuts import render
from .models import Table, Booking
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime


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

def make_booking(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        date = request.POST['date']
        time = request.POST['time']
        guests = int(request.POST['guests'])

        allocated = available_tables(date, time, guests)
        if not allocated:
            return JsonResponse({'error': 'No available tables'}, status=400)

        booking = Booking.objects.create(
            name=name,
            email=email,
            phone=phone,
            date=date,
            time=time,
            guests=guests
        )
        booking.tables.set(allocated)
        booking.save()

        return JsonResponse({'success': 'Booking confirmed!'})
    
    return render(request, 'booking_form.html')