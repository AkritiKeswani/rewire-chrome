from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

# Create your views here.
def index(request):
    if request.user.is_authenticated and request.user.is_active:
        return redirect('landing')
    else:
        return render(request, 'app/index.html')


