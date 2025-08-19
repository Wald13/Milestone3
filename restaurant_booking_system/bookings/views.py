from django.shortcuts import render
from .models import Table, Booking
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
    
    return None  # If not enough tables

def make_booking(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        date = request.POST['date']
        time = request.POST['time']
        guests = int(request.POST['guests'])

        # Validate date and time
        booking_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')

        # Check if the booking is in the past
        if booking_datetime < datetime.now():
            return render(request, 'booking_form.html', {
                'error': 'Cannot book a table in the past.'
            })

        allocated = available_tables(date, time, guests)
        if not allocated:
            return render(request, 'booking_form.html', {
                'error': 'No available tables for this time. Please choose another time.'
                })

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

        return render(request, 'Booking confirmed!', {
            'success': f'Booking confirmed for {name}!'  
        })
    
    return render(request, 'booking_form.html')

