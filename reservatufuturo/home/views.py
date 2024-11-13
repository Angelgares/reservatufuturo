from django.shortcuts import render
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'home/login.html'

def homepage(request):
    return render(request, 'home/homepage.html')
