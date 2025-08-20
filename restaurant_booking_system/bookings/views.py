from django.shortcuts import render
from .models import Table, Booking
from datetime import datetime

def available_tables(date, time, guests):
    booked_tables = Booking.objects.filter(
        date=date,
        time=time
    ).values_list('tables', flat=True)
    available = Table.objects.exclude(id__in=booked_tables).order_by('seats')
    
    seats_needed = guests
    tables_allocated = []
    for table in available:
        tables_allocated.append(table)
        seats_needed -= table.seats
        if seats_needed <= 0:
            return tables_allocated
    return None

def make_booking(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        date = request.POST['date']
        time = request.POST['time']
        guests = int(request.POST['guests'])

         # Validate date and time
        booking_datetime = datetime.strptime(f"{date} {time_str}", '%Y-%m-%d %H:%M')

        # Check if the booking is in the past
        if booking_datetime < datetime.now():
            return render(request, 'booking_form.html', {
                'error': 'Please choose a future date and time.'
            })

        # Check if the minutes are in 15-minute intervals
        if booking_datetime.minute % 15 != 0:
            return render(request, 'booking_form.html', {
                'error': 'Please select a time in 15-minute intervals (e.g., 12:00, 12:15, 12:30).'
            })

        allocated = available_tables(date, time_str, guests)
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

        return render(request, 'booking_form.html', {
            'success': f'Booking confirmed for {name}!'
        })

    return render(request, 'booking_form.html')


def cancel_booking(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']

        booking = Booking.objects.filter(email=email, phone=phone).first()

        if not booking:
            return render(request, 'cancel_booking.html', {
                'error': 'No booking found with the provided details.'
            })
        
        booking.delete()
        return render(request, 'cancel_booking.html', {
            'success': 'Booking cancelled successfully.'
        })

    return render(request, 'cancel_booking.html')

