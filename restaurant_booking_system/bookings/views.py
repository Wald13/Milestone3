from django.shortcuts import render
from .models import Table, Booking
from datetime import datetime, timedelta

# Function to find available tables
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

# Booking form view
def make_booking(request):
    # Generate 15-minute interval times from 12:00 to 22:00
    times = []
    start = datetime.strptime("12:00", "%H:%M")
    end = datetime.strptime("22:00", "%H:%M")
    current = start
    while current <= end:
        times.append(current.strftime("%H:%M"))
        current += timedelta(minutes=15)

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        date = request.POST['date']
        time_str = request.POST['time']
        guests = int(request.POST['guests'])

        # Validate date and time
        booking_datetime = datetime.strptime(f"{date} {time_str}", '%Y-%m-%d %H:%M')

        # Check if the booking is in the past
        if booking_datetime < datetime.now():
            return render(request, 'booking_form.html', {
                'times': times,
                'error': 'Please choose a future date and time.'
            })

        # Check if the minutes are in 15-minute intervals
        if booking_datetime.minute % 15 != 0:
            return render(request, 'booking_form.html', {
                'times': times,
                'error': 'Please select a time in 15-minute intervals (e.g., 12:00, 12:15, 12:30).'
            })

        allocated = available_tables(date, time_str, guests)
        if not allocated:
            return render(request, 'booking_form.html', {
                'times': times,
                'error': 'No available tables for this time. Please choose another time.'
            })

        booking = Booking.objects.create(
            name=name,
            email=email,
            phone=phone,
            date=date,
            time=time_str,
            guests=guests
        )
        booking.tables.set(allocated)
        booking.save()

        return render(request, 'booking_form.html', {
            'times': times,
            'success': f'Booking confirmed for {name}!'
        })

    return render(request, 'bookings/booking_form.html', {'times': times})

# Cancel booking view
def cancel_booking(request):
    context = {}
    
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']

        booking = Booking.objects.filter(email=email, phone=phone).first()

        if not booking:
            context['error'] = 'No booking found with the provided details.'
        else:
            booking.delete()
            context['success'] = 'Booking cancelled successfully.'
    
    return render(request, 'bookings/cancel_booking.html', context)


# Homepage view
def home(request):
    return render(request, 'bookings/home.html')

def menu(request):
    return render(request, 'bookings/menu.html')  

def contact(request):
    return render(request, 'bookings/contact.html')
