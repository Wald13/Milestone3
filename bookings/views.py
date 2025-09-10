from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.db.models import Q
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

def custom_logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# Booking and Dashboard Views
@login_required
def dashboard(request):
    bookings = Booking.objects.filter(Q(user=request.user) | Q(email=request.user.email)).order_by('date', 'time')
    return render(request, 'bookings/dashboard.html', {'bookings': bookings})

@login_required
def my_bookings(request, booking_id):
    booking = get_object_or_404(Booking,Q(id=booking_id, user=request.user) | Q(id=booking_id, email=request.user.email))
    return render(request, 'bookings/my_bookings.html', {'booking': booking})

@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, Q(id=booking_id, user=request.user) | Q(id=booking_id, email=request.user.email))
    
    # Generate times for the form
    times = []
    start = time(12, 0)
    end = time(22, 30)
    interval = timedelta(minutes=15)
    current = datetime.combine(datetime.min, start)
    while current.time() <= end:
        times.append(current.strftime('%H:%M'))
        current += interval
    
    if request.method == 'POST':
        form = BookingEditForm(request.POST, instance=booking)
        if form.is_valid():
            # Correct fix: The form has already converted the time to a datetime.time object.
            # No need for strptime().
            booking_date = form.cleaned_data['date']
            booking_time = form.cleaned_data['time']
            
            # Combine date and time to check against current time
            booking_datetime = datetime.combine(booking_date, booking_time)

            if booking_datetime < datetime.now():
                messages.error(request, 'Cannot edit a booking for a past date and time.')
                return render(request, 'bookings/edit_booking.html', {'form': form, 'booking': booking, 'times': times})

            # Check table availability (excluding the current booking)
            guests = form.cleaned_data['guests']
            available = available_tables(booking_date, booking_time, guests, exclude_booking=booking)
            
            if not available:
                messages.error(request, f'No available tables for {guests} guests at {booking_time.strftime("%H:%M")} on {booking_date}. Please choose another time.')
                return render(request, 'bookings/edit_booking.html', {'form': form, 'booking': booking, 'times': times})

            # Update booking and tables
            updated_booking = form.save()
            updated_booking.tables.set(available)
            
            messages.success(request, 'Booking updated successfully!')
            return redirect('dashboard')
        else:
            # If the form is not valid, re-render the page with the form object
            # that contains the validation errors.
            return render(request, 'bookings/edit_booking.html', {'form': form, 'booking': booking, 'times': times})
    else:
        form = BookingEditForm(instance=booking)
    
    return render(request, 'bookings/edit_booking.html', {'form': form, 'booking': booking, 'times': times})

@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, Q(id=booking_id, user=request.user) | Q(id=booking_id, email=request.user.email))
    
    if request.method == 'POST':
        booking_info = f"{booking.name} on {booking.date} at {booking.time}"
        booking.delete()
        messages.success(request, f'Booking for {booking_info} has been cancelled.')
        return redirect('dashboard')
    
    return render(request, 'bookings/confirm_delete.html', {'booking': booking})

def make_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Check table availability
            booking_date = form.cleaned_data['date']
            booking_time = form.cleaned_data['time']
            guests = form.cleaned_data['guests']

            # Use the available_tables function from utils.py
            allocated = available_tables(booking_date, booking_time, guests)
            
            if not allocated:
                messages.error(request, f'No available tables for {guests} guests at {booking_time.strftime("%H:%M")} on {booking_date}.')
                return render(request, 'bookings/booking_form.html', {'form': form})

            # Create and save the booking
            booking = form.save(commit=False)
            booking.user = request.user if request.user.is_authenticated else None
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
    
    # Generate times for the form
    times = []
    start = time(12, 0)
    end = time(22, 30)
    interval = timedelta(minutes=15)
    current = datetime.combine(datetime.min, start)
    while current.time() <= end:
        times.append(current.strftime('%H:%M'))
        current += interval

    context = {
        'form': form,
        'times': times,
    }
    return render(request, 'bookings/booking_form.html', context)


# General pages
def home(request):
    return render(request, 'bookings/home.html')

def menu(request):
    return render(request, 'bookings/menu.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # ContactMessage.objects.create(name=name, email=email, message=message)
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('contact')
    return render(request, 'bookings/contact.html')

def cancel_booking_unauthenticated(request):
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
            return redirect('cancel_booking_unauthenticated')
    
    return render(request, 'bookings/cancel_booking_unauthenticated.html')
