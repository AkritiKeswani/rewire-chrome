from django.urls import path

from . import views

authpatterns = []                       #routes for authentication

urlpatterns = [] + authpatterns         # routes for the app
