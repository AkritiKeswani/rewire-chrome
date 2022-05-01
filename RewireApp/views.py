import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.debug import sensitive_post_parameters, sensitive_variables
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from RewireApp.forms import AuthenticationForm, CustomUserCreationForm, UpdateUserForm
from RewireApp.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UpdateUserSerializer,
)

logger = logging.getLogger(__name__)

# web app views
def index(request):
    if request.user.is_authenticated and request.user.is_active:
        return redirect("app_landing")
    else:
        return render(request, "app/base.html", context={})


@login_required()
def landing(request):
    return render(request, "app/landing.html", context={})


@sensitive_variables("user_instance")
@sensitive_post_parameters()
@transaction.atomic
def signup(request):
    if request.user.is_authenticated and request.user.is_active:
        return redirect("index")

    if request.method == "POST":
        creation_form = CustomUserCreationForm(request.POST or None)

        if creation_form.is_valid():
            user_instance = creation_form.save()
            login(request, user_instance)
            messages.success(request, "Your account was created successfully.")
            return redirect("app_landing")
        else:
            messages.error(request, "There was an error creating the profile because:")
            logger.info("signup form invalidated.")
    else:
        creation_form = CustomUserCreationForm(request.POST or None)

    return render(
        request,
        "auth/signup.html",
        {"page_name": "Life Nest | Sign Up", "creation": creation_form},
    )


@transaction.atomic
@sensitive_post_parameters()
@sensitive_variables()
@login_required
def update_password(request):
    if request.user.is_authenticated and request.user.is_active:
        if request.method == "POST":
            password_change_form = PasswordChangeForm(
                request.user, request.POST or None
            )

            if password_change_form.is_valid():
                user = password_change_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully changed.")
                return redirect("landing")
            else:
                messages.error(request, "Error updating your password.")
        else:
            password_change_form = PasswordChangeForm(
                request.user, request.POST or None
            )
        return render(
            request,
            "auth/change_password.html",
            {
                "page_name": "Life Nest | Password Change",
                "password_change": password_change_form,
            },
        )
    else:
        return redirect("index")


@transaction.atomic
@sensitive_post_parameters()
@login_required
def update_profile(request):
    if request.user.is_authenticated and request.user.is_active:
        user_update_form = UpdateUserForm(request.POST or None, instance=request.user)
        if request.POST and user_update_form.is_valid():
            user_instance = user_update_form.save()
            return redirect("index")
        else:
            return render(
                request,
                "app/edit_profile.html",
                {"page_name": "Life Nest | Edit Profile", "creation": user_update_form},
            )
    else:
        return redirect("index")


@login_required
def signout(request):
    logout(request)
    return redirect("index")


@login_required
def delete_data(request):
    if request.user.is_authenticated and request.user.is_active:
        User.objects.get(username=request.user.get_username()).delete()
        logout(request)
        logger.warning("An account was deleted by the user himself.")
    return redirect("index")


@transaction.atomic
@sensitive_post_parameters()
@sensitive_variables("username", "password", "user")
def signin(request):
    if request.user.is_authenticated and request.user.is_active:
        return redirect("index")

    if request.method == "POST":
        authentication_form = AuthenticationForm(request.POST or None)

        if authentication_form.is_valid():
            username = authentication_form.cleaned_data.get("username")
            password = authentication_form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if not user:
                authentication_form.add_error(
                    field="password", error="Incorrect password for the username."
                )
            else:
                login(request, user)
                return redirect("app_landing")
    else:
        authentication_form = AuthenticationForm(request.POST or None)

    return render(
        request,
        "auth/login.html",
        {"page_name": "Life Nest | Sign In", "authentication": authentication_form},
    )


# API views
class CustomObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class ChangePasswordView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer


class UpdateProfileView(generics.UpdateAPIView):

    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserSerializer


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
