# config/urls.py
from django.contrib import admin
from django.urls import include, path  # new
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from RewireApp.views import (
    ChangePasswordView,
    CustomObtainTokenPairView,
    RegisterView,
    UpdateProfileView,
    LogoutView,
    LogoutAllView,
)

# api routing
router = DefaultRouter()


# app routing
authpatterns = [
    path("login/", CustomObtainTokenPairView.as_view(), name="token_obtain_pair"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="auth_register"),
    path(
        "change_password/<int:pk>/",
        ChangePasswordView.as_view(),
        name="auth_change_password",
    ),
    path(
        "update_profile/<int:pk>/",
        UpdateProfileView.as_view(),
        name="auth_update_profile",
    ),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
    path("logout_all/", LogoutAllView.as_view(), name="auth_logout_all"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # new
] + authpatterns  # routes for the app
