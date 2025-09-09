from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking
from datetime import datetime, timedelta

class CustomerUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class BookingForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'date', 'time', 'guests']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'class': 'form-control'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        times = []
        start = datetime.strptime("12:00", "%H:%M")
        end = datetime.strptime("22:00", "%H:%M")
        current = start
        while current <= end:
            time_str = current.strftime("%H:%M")
            times.append((time_str, time_str))
            current += timedelta(minutes=15)
        
        self.fields['time'].widget = forms.Select(choices=times, attrs={'class': 'form-control'})

class BookingEditForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Booking
        fields = ['name', 'email', 'phone', 'date', 'time', 'guests']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'class': 'form-control'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '20'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        times = []
        start = datetime.strptime("12:00", "%H:%M")
        end = datetime.strptime("22:00", "%H:%M")
        current = start
        while current <= end:
            time_str = current.strftime("%H:%M")
            times.append((time_str, time_str))
            current += timedelta(minutes=15)
        
        self.fields['time'].widget = forms.Select(choices=times, attrs={'class': 'form-control'})
