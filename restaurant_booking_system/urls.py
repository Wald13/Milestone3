from django.contrib import admin
from django.urls import path
from bookings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('contact/', views.contact, name='contact'),
    path('book/', views.make_booking, name='make_booking'),
    path('cancel/', views.cancel_booking_unauthenticated, name='cancel_booking_unauthenticated'),
    path('my_bookings/', views.dashboard, name='my_bookings'),
     # Authentication URLs
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.custom_logout_view, name='logout'),
    # User Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('booking/<int:booking_id>/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('booking/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
]