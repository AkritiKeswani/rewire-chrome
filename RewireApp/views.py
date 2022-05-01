from django.shortcuts import render
import logging

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny

from RewireApp.serializers import CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)

# Create your views here.
class CustomObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer
