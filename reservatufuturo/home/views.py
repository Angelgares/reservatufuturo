from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
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
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            login(request, user)
            return redirect('homepage')
    else:
        form = RegistrationForm()
    return render(request, 'home/register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'home/profile.html')