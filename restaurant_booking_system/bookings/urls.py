from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.make_booking, name='make_booking'),
    path('cancel/', views.cancel_booking, name='cancel_booking'),
]