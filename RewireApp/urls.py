# config/urls.py
from django.contrib import admin
from django.urls import path, include  # new
from . import views


authpatterns = []  # routes for authentication

urlpatterns = [
    path("", views.index, name='index'),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # new
] + authpatterns  # routes for the app
