from django.contrib import admin
from django.urls import path
from ..bookings import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('contact/', views.contact, name='contact'),
    path('book/', views.make_booking, name='make_booking'),
    path('cancel/', views.cancel_booking, name='cancel_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:pk>/edit/', views.edit_booking, name='edit_booking'),

]