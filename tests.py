from django.test import TestCase

# Create your tests here.
# Test if gunicorn works locally
gunicorn restaurant_booking_system.wsgi:application
