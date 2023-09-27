from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home')
]
