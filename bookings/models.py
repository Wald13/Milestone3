from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Models for the restaurant booking system
class Table(models.Model):
    number = models.IntegerField(unique=True)
    seats = models.IntegerField()

    def __str__(self):
        return f"Table {self.number} ({self.seats} seats)"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()
    guests = models.IntegerField()
    tables = models.ManyToManyField(Table, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"
    def get_absolute_url(self):
        return reverse('booking_detail', args=[self.id])

    class Meta:
        ordering = ['-created_at']
        
class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=50)

    def __str__(self):
        return self.name