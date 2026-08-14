from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def login_view(request):
    return render(request, 'accounts/login.html')