from django.contrib import admin

# Models for the restaurant booking system as admin interface
from .models import Table, Booking, MenuItem

admin.site.register(Table)
admin.site.register(Booking)
admin.site.register(MenuItem)