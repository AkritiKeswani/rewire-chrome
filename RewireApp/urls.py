# config/urls.py
from django.contrib import admin
from django.urls import include, path  # new
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from RewireApp.views import CustomObtainTokenPairView

# api routing
router = DefaultRouter()


# app routing
authpatterns = []  # routes for authentication

jwtpatterns = [
    path("token/", CustomObtainTokenPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns = (
    [
        path("", include(router.urls)),
        path("admin/", admin.site.urls),
        path("accounts/", include("django.contrib.auth.urls")),  # new
    ]
    + authpatterns
    + jwtpatterns
)  # routes for the app
