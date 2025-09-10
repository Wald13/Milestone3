from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .models import Table, Booking
from .forms import CustomerUserCreationForm, BookingForm, BookingEditForm
from datetime import datetime, time, timedelta
from .utils import available_tables



# Authentication Views
class CustomLoginView(LoginView):
    template_name = 'bookings/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

class RegisterView(CreateView):
    form_class = CustomerUserCreationForm
    template_name = 'bookings/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        messages.success(self.request, f'Welcome {user.first_name}! Your account has been created.')
        return response

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-date', '-time')
    return render(request, 'bookings/dashboard.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    start_time = time(12, 0)  # 12:00 PM
    end_time = time(22, 30)   # 10:30 PM
    interval = timedelta(minutes=15) # 15-minute intervals
    times = []
    current_time = datetime.combine(datetime.min, start_time)
    while current_time.time() <= end_time:
        times.append(current_time.strftime('%H:%M'))
        current_time += interval
    
    if request.method == 'POST':
        form = BookingEditForm(request.POST, instance=booking)
        if form.is_valid():
            # Check if the booking is in the past
            booking_date = form.cleaned_data['date']
            booking_time_str = form.cleaned_data['time']
            booking_time = datetime.strptime(booking_time_str, '%H:%M').time()
            booking_datetime = datetime.combine(booking_date, booking_time)

            if booking_datetime < datetime.now():
                messages.error(request, 'Cannot edit booking for a past date and time.')
                return render(request, 'bookings/edit_booking.html', {'form': form, 'booking': booking, 'times': times})

            # Check table availability (excluding current booking)
            guests = form.cleaned_data['guests']
            available = available_tables(booking_date, booking_time, guests, exclude_booking=booking)
            
            if not available:
                messages.error(request, f'No available tables for {guests} guests at {booking_time_str} on {booking_date}. Please choose another time.')
                return render(request, 'bookings/edit_booking.html', {'form': form, 'booking': booking, 'times': times})

            # Update booking
            updated_booking = form.save()
            updated_booking.tables.set(available)
            updated_booking.save()
            
            messages.success(request, 'Booking updated successfully!')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingEditForm(instance=booking)
    
    return render(request, 'bookings/edit_booking.html', {'form': form, 'booking': booking, 'times': times})

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking_info = f"{booking.name} on {booking.date} at {booking.time}"
        booking.delete()
        messages.success(request, f'Booking for {booking_info} has been cancelled.')
        return redirect('dashboard')
    
    return render(request, 'bookings/confirm_delete.html', {'booking': booking})

# Make_booking view
def make_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Check table availability
            booking_date = form.cleaned_data['date']
            booking_time_str = form.cleaned_data['time']
            guests = form.cleaned_data['guests']

            # Use the available_tables function from utils.py
            allocated = available_tables(booking_date, booking_time_str, guests)
            
            if not allocated:
                messages.error(request, f'No available tables for {guests} guests at {booking_time_str} on {booking_date}.')
                return render(request, 'bookings/booking_form.html', {'form': form})

            # Create and save the booking
            booking = form.save(commit=False)
            booking.user = request.user if request.user.is_authenticated else None
            booking.time = booking_time_str
            booking.save()
            booking.tables.set(allocated)

            if request.user.is_authenticated:
                messages.success(request, 'Booking confirmed! You can view and manage it in your dashboard.')
                return redirect('dashboard')
            else:
                messages.success(request, f'Booking confirmed for {booking.name}! Create an account to manage your bookings.')
                return redirect('make_booking')
    else:
        form = BookingForm()
    
    start_time = time(12, 0)  # 12:00 PM
    end_time = time(22, 30)   # 10:30 PM
    interval = timedelta(minutes=15) # 15-minute intervals

    times = []
    current_time = datetime.combine(datetime.min, start_time)
    while current_time.time() <= end_time:
        times.append(current_time.strftime('%H:%M'))
        current_time += interval

    context = {
        'form': form,
        'times': times,
    }
    return render(request, 'bookings/booking_form.html', context)
def custom_logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Keep existing views
def cancel_booking(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']
        booking = Booking.objects.filter(email=email, phone=phone).first()

        if not booking:
            messages.error(request, 'No booking found with the provided details.')
        else:
            booking_info = f"{booking.name} on {booking.date} at {booking.time}"
            booking.delete()
            messages.success(request, f'Booking for {booking_info} has been cancelled.')
            return redirect('cancel_booking')
    
    return render(request, 'bookings/cancel_booking.html')

def home(request):
    return render(request, 'bookings/home.html')

def menu(request):
    return render(request, 'bookings/menu.html')

def contact(request):
    return render(request, 'bookings/contact.html')
