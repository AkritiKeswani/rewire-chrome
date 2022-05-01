from django.contrib.auth.models import User


def user_auth_context(request):
    context = dict()
    if request.user.is_authenticated and request.user.is_active:
        context["logged_in"] = True
        context["current_user"] = request.user
        context["full_name"] = request.user.get_full_name()
        context["first_name"] = request.user.first_name
    else:
        context["logged_in"] = False
        context["current_user"] = request.user
    return context
