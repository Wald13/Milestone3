from django.shortcuts import render
from django.contrib import messages
from .models import Table, Booking
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect


# Function to find available tables
def available_tables(date, time, guests):
    booked_tables = Booking.objects.filter(
        date=date,
        time=time
    ).values_list('tables__id', flat=True)
    available = Table.objects.exclude(id__in=booked_tables).order_by('seats')
    
    seats_needed = guests
    tables_allocated = []
    for table in available:
        tables_allocated.append(table)
        seats_needed -= table.seats
        if seats_needed <= 0:
            return tables_allocated
    return None

    # Edit booking view
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Generate 15-minute interval times from 12:00 to 22:00 (same as make_booking)
    times = []
    start = datetime.strptime("12:00", "%H:%M")
    end = datetime.strptime("22:00", "%H:%M")
    current = start
    while current <= end:
        times.append(current.strftime("%H:%M"))
        current += timedelta(minutes=15)

    if request.method == "POST":
        booking.name = request.POST["name"]
        booking.email = request.POST["email"]
        booking.phone = request.POST["phone"]
        booking.date = datetime.strptime(request.POST["date"], "%Y-%m-%d").date()
        booking.time = datetime.strptime(request.POST["time"], "%H:%M").time()
        booking.guests = int(request.POST["guests"])
        booking.save()

        messages.success(request, "✅ Booking updated successfully!")
        return redirect("my_bookings")

    return render(request, "bookings/edit_booking.html", {
        "booking": booking,
        "times": times
    })

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

        # Convert to Python datetime
        booking_date = datetime.strptime(date, "%Y-%m-%d").date()
        booking_time = datetime.strptime(time_str, "%H:%M").time()

        # Assume booking lasts 2 hours
        start_dt = datetime.combine(booking_date, booking_time)
        end_dt = start_dt + timedelta(hours=2)

        # Find all tables that can fit the party size
        candidate_tables = Table.objects.filter(seats__gte=guests)

        # Exclude tables already booked in the same time slot
        unavailable = Booking.objects.filter(
            date=booking_date,
            time__lt=end_dt.time()
        ).exclude(time__gte=booking_time)

        taken_tables = Table.objects.filter(booking__in=unavailable).distinct()
        free_tables = candidate_tables.exclude(id__in=taken_tables)

        if not free_tables.exists():
            messages.error(request, "⚠️ Sorry, no tables available for that time and party size.")
        else:
            # Pick the first available table (or you could let user pick)
            table = free_tables.first()
            booking = Booking.objects.create(
                name=name,
                email=email,
                phone=phone,
                date=booking_date,
                time=booking_time,
                guests=guests
            )
            booking.tables.add(table)
            messages.success(request, f"✅ Your booking is confirmed at Table {table.number}!")
            return redirect('home')

    return render(request, 'bookings/booking_form.html', {"times": times})

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

#  Just a return a template
def my_bookings(request):
    return render(request, "bookings/my_bookings.html")