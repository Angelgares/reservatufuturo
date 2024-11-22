from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .forms import EmailAuthenticationForm
from .models import Reservation, Course
from collections import defaultdict
from django.conf import settings


class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'home/login.html'


def homepage(request):
    template_name = 'home/homepage.html'
    courses = Course.objects.all()

    # Agregar la URL de la imagen al contexto
    courses_with_images = [
        {
            **course.__dict__,
            'image_url': get_image_url(course.image)
        }
        for course in courses
    ]

    context = {
        'courses': courses_with_images
    }
    return render(request, template_name, context)


def about_us(request):
    return render(request, 'home/about_us.html')


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


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'home/edit_profile.html', context)


@login_required
def my_courses(request):
    reservas = Reservation.objects.filter(user=request.user).exclude(paymentMethod='Pending')
    cursos = [
        {
            **reserva.course.__dict__,
            'image_url': get_image_url(reserva.course.image)
        }
        for reserva in reservas if not reserva.cart
    ]

    return render(request, 'courses/my_courses.html', {'cursos': cursos})


def get_image_url(image):
    """
    Devuelve la URL completa de la imagen o la predeterminada si no hay imagen.
    """
    if image:
        return f"{settings.MEDIA_URL}{image}"
    return f"{settings.STATIC_URL}home/course_images/default_course_image.jpg"
