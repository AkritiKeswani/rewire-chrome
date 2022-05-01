# config/urls.py
from django.contrib import admin
from django.urls import include, path  # new
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import views as auth_views

from RewireApp.views import (
    ChangePasswordView,
    CustomObtainTokenPairView,
    RegisterView,
    UpdateProfileView,
    LogoutView,
    LogoutAllView,
    index,
    signup,
    signin,
    landing,
    signout,
    update_password,
    update_profile,
    delete_data,
)

# api routing
router = DefaultRouter()


# password reset
password_reset_patterns = [
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

# web app
web = [
    path("app/auth/signup/", signup, name="app_auth_signup"),
    path("app/auth/signin/", signin, name="app_auth_signin"),
    path("app/auth/signout/", signout, name="app_auth_signout"),
    path("app/landing", landing, name="app_landing"),
    path("app/update_profile/", update_profile, name="app_update_profile"),
    path("app/password_change/", update_password, name="app_password_change"),
    path("app/delete_data/", delete_data, name="app_delete_data"),
]


# app routing
authpatterns = [
    path("api/login/", CustomObtainTokenPairView.as_view(), name="token_obtain_pair"),
    path("api/login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="auth_register"),
    path(
        "api/change_password/<int:pk>/",
        ChangePasswordView.as_view(),
        name="auth_change_password",
    ),
    path(
        "api/update_profile/<int:pk>/",
        UpdateProfileView.as_view(),
        name="auth_update_profile",
    ),
    path("api/logout/", LogoutView.as_view(), name="auth_logout"),
    path("api/logout_all/", LogoutAllView.as_view(), name="auth_logout_all"),
]

urlpatterns = (
    [
        path("", index, name="index"),
        path("authed/", include(router.urls)),
        path("admin/", admin.site.urls),
        path("accounts/", include("django.contrib.auth.urls")),  # new
    ]
    + authpatterns
    + web
    + password_reset_patterns
)  # routes for the app
