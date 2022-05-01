from ast import Delete
import logging
import datetime
from black import re

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.db.models import Q
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
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from RewireApp.forms import (
    AuthenticationForm,
    CustomUserCreationForm,
    UpdateUserForm,
    AddMoneyForm,
    EmailForm,
    AddWebsiteForm,
    DeleteWebsiteForm,
)
from RewireApp.serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    FlowSerializer,
    RegisterSerializer,
    UpdateUserSerializer,
    BlocklistSerializer,
    FriendSerializer,
)
from RewireApp.models import Participant, Blocklist, Friend, Flow

logger = logging.getLogger(__name__)

# web app views
def index(request):
    if request.user.is_authenticated and request.user.is_active:
        return redirect("app_landing")
    else:
        return render(
            request, "app/base.html", context={"page_name": "ReWire | Welcome"}
        )


@login_required()
def landing(request):
    blocked_websites = Blocklist.objects.filter(user__user=request.user).all()
    focus_sessions = (
        Flow.objects.filter(user__user=request.user).order_by("start_time").all()
    )

    friends_q = Friend.objects.filter(
        Q(sender__pk=request.user.pk) | Q(receiver__pk=request.user.pk)
    ).all()
    friends = list()
    for f in friends_q:
        if f.sender.user.pk == request.user.pk:
            friends.append(f.receiver)
        elif f.receiver.user.pk == request.user.pk:
            friends.append(f.sender)
    if request.method == "POST":
        add_website_form = AddWebsiteForm(request.POST or None)
        delete_website_form = DeleteWebsiteForm(request.POST or None)

        if add_website_form.is_valid():
            blocklist_instance = Blocklist.objects.create(
                user=Participant.objects.get(user=request.user),
                website=add_website_form.cleaned_data.get("add_website"),
            )
            blocklist_instance.save(force_insert=True)

        if delete_website_form.is_valid():
            blocklist_instance = Blocklist.objects.filter(
                user=Participant.objects.get(user=request.user),
                website=add_website_form.cleaned_data.get("delete_website"),
            ).first()
            if blocklist_instance:
                blocklist_instance.delete()

    else:
        add_website_form = AddWebsiteForm(request.POST or None)
        delete_website_form = DeleteWebsiteForm(request.POST or None)

    return render(
        request,
        "app/landing.html",
        context={
            "page_name": "ReWire | Welcome",
            "blocked_websites": blocked_websites,
            "focus_sessions": focus_sessions,
            "friends": friends,
            "add_website_form": add_website_form,
            "delete_website_form": delete_website_form,
        },
    )


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
            participant = Participant.objects.create(user=user_instance)
            participant.save(force_insert=True)
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
        {"page_name": "ReWire | Sign Up", "creation": creation_form},
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
                participant_instance = Participant.objects.get(user=request.user)
                user = password_change_form.save()
                participant_instance.user = user
                participant_instance.save()
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
                "page_name": "ReWire | Password Change",
                "password_change": password_change_form,
            },
        )
    else:
        return redirect("index")


@transaction.atomic
@sensitive_post_parameters()
@login_required
def add_money(request):
    if request.user.is_authenticated and request.user.is_active:
        add_money_form = AddMoneyForm(request.POST or None)
        if request.POST and add_money_form.is_valid():
            participant_instance = Participant.objects.get(user=request.user)
            participant_instance.money = add_money_form.cleaned_data.get("balance")
            participant_instance.save()
            return redirect("index")
        else:
            return render(
                request,
                "app/add_money.html",
                {"page_name": "ReWire | Add Balance", "money": add_money_form},
            )
    else:
        return redirect("index")


@transaction.atomic
@sensitive_post_parameters()
@login_required()
def add_friend(request):
    if request.user.is_authenticated and request.user.is_active:
        add_friend_form = EmailForm(request.POST or None)
        if request.POST and add_friend_form.is_valid():
            friend_sender_instance = Participant.objects.get(user=request.user)
            friend_receiver_instance = Participant.objects.get(
                user__email=add_friend_form.cleaned_data.get("email")
            )
            friend_object_instance = Friend.objects.create(
                sender=friend_sender_instance, receiver=friend_receiver_instance
            )
            friend_object_instance.save()
            return redirect("index")
        else:
            return render(
                request,
                "app/add_friend.html",
                {"page_name": "ReWire | Add a Friend", "friend": add_friend_form},
            )
    else:
        return redirect("index")


@transaction.atomic
@sensitive_post_parameters()
@login_required
def update_profile(request):
    if request.user.is_authenticated and request.user.is_active:
        add_friend_form = EmailForm(request.POST or None)
        add_money_form = AddMoneyForm(request.POST or None)
        user_update_form = UpdateUserForm(request.POST or None, instance=request.user)
        if (
            request.POST
            and user_update_form.is_valid()
            and add_friend_form.is_valid()
            and add_money_form.is_valid()
        ):
            # friend form
            friend_sender_instance = Participant.objects.get(user=request.user)
            friend_receiver_instance = Participant.objects.get(
                user__email=add_friend_form.cleaned_data.get("email")
            )
            friend_object_instance = Friend.objects.create(
                sender=friend_sender_instance, receiver=friend_receiver_instance
            )
            friend_object_instance.save()
            # user update form
            participant_instance = Participant.objects.get(user=request.user)
            user_instance = user_update_form.save()
            participant_instance.user = user_instance
            participant_instance.money = add_money_form.cleaned_data.get("balance")
            participant_instance.save()
            return redirect("index")
        else:
            return render(
                request,
                "app/edit_profile.html",
                {
                    "page_name": "ReWire | Edit Profile",
                    "creation": user_update_form,
                    "money": add_money_form,
                    "friend": add_friend_form,
                },
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
        {"page_name": "ReWire | Sign In", "authentication": authentication_form},
    )


# API views
class FlowViewSet(ModelViewSet):

    queryset = Friend.objects.all()
    serializer_class = FlowSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["post"])
    def new_flow(self, request):
        participant_instance = Participant.objects.get(user__pk=request.user.pk)
        accountability_dude_instance = Participant.objects.filter(
            user__username=request.data.get("accountable_dude")
        ).first()
        if not accountability_dude_instance:
            return Response(
                "'accountability_dude' not found.", status.HTTP_400_BAD_REQUEST
            )

        flow_instance = Flow.objects.create(
            user=participant_instance,
            accountable_dude=accountability_dude_instance,
            start_time=request.data.get("start_time"),
            end_time=request.data.get("end_time"),
            money=int(request.data.get("money")),
            success=True if request.data.get("success") == "true" else False,
        )
        flow_instance.save()
        # update money
        curr_money = participant_instance.money
        if not flow_instance.success:
            participant_instance.money = max(0, (curr_money - flow_instance.money))
            participant_instance.save()
        resp = {
            "user": request.user.username,
            "accountable_dude": flow_instance.accountable_dude.user.username,
            "start_time": str(flow_instance.start_time),
            "end_time": str(flow_instance.end_time),
            "money": flow_instance.money,
            "success": flow_instance.success,
            "remaining_money": participant_instance.money,
        }
        return Response(resp, status.HTTP_201_CREATED)


class BlocklistViewSet(ReadOnlyModelViewSet):

    queryset = Blocklist.objects.all()
    serializer_class = BlocklistSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"])
    def get_blocked(self, request):
        data = self.queryset.filter(user__pk=request.user.pk)
        serializer = self.get_serializer(data, many=True)
        return Response(serializer.data)


class FriendViewSet(ReadOnlyModelViewSet):

    queryset = Friend.objects.all()
    serializer_class = FriendSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=["get"])
    def get_friends(self, request):
        data = self.queryset.filter(
            Q(sender__pk=request.user.pk) | Q(receiver__pk=request.user.pk)
        )
        serialized = list()
        for f in data:
            if f.sender.user.pk == request.user.pk:
                serialized.append(
                    {
                        "user_id": f.receiver.user.pk,
                        "username": f.receiver.user.username,
                        "email": f.receiver.user.email,
                        "first_name": f.receiver.user.first_name,
                        "last_name": f.receiver.user.last_name,
                        "full_name": f.receiver.full_name,
                    }
                )
            elif f.receiver.user.pk == request.user.pk:
                serialized.append(
                    {
                        "user_id": f.sender.user.pk,
                        "username": f.sender.user.username,
                        "email": f.sender.user.email,
                        "first_name": f.sender.user.first_name,
                        "last_name": f.sender.user.last_name,
                        "full_name": f.sender.full_name,
                    }
                )
        return Response(serialized)


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
