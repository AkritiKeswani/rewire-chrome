from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "email",
        )


class AuthenticationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username_entry = self.cleaned_data["username"]
        try:
            user = User.objects.get(username=username_entry)
            if not user.is_active:
                raise forms.ValidationError(
                    "The account for this user has been deactivated."
                )
        except User.DoesNotExist as ex:
            raise forms.ValidationError("The user does not exist.")
        return username_entry


class UpdateUserForm(UserChangeForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
        )
