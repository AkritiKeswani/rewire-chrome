# config/urls.py
from django.contrib import admin
from django.urls import include, path  # new
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from RewireApp.views import CustomObtainTokenPairView, RegisterView

# api routing
router = DefaultRouter()


# app routing
authpatterns = [
    path("login/", CustomObtainTokenPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="auth_register"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # new
] + authpatterns  # routes for the app
