from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required


class CustomLoginView(LoginView):
    template_name = 'home/login.html'

def homepage(request):
    return render(request, 'home/homepage.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('homepage')
    else:
        form = RegistrationForm()
    return render(request, 'home/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'home/profile.html')