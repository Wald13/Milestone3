from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('contact/', views.contact, name='contact'),
    path('book/', views.make_booking, name='make_booking'),
    path('cancel/', views.cancel_booking, name='cancel_booking'),
]