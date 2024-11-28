from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .forms import EmailAuthenticationForm
from .models import Reservation, Course
from django.conf import settings
from django.utils import timezone
from django.db.models import Q


def base_view(request):
    cart_item_count = Reservation.objects.filter(user=request.user, cart=True).count() if request.user.is_authenticated else 0
    return {
        'cart_item_count': cart_item_count,
    }


class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = 'home/login.html'


def homepage(request):
    template_name = 'home/homepage.html'
    current_date = timezone.now().date()

    name_query = request.GET.get('name_search', '')
    type_query = request.GET.get('type_search', '')
    date_query = request.GET.get('date_search', '')

    # Filtrar cursos cuya fecha de inicio es igual o posterior a la fecha actual
    courses = Course.objects.filter(starting_date__gte=current_date).order_by('-starting_date')

    # Aplicar filtros
    if name_query:
        courses = courses.filter(Q(name__icontains=name_query))
    if date_query:
        courses = courses.filter(Q(starting_date__icontains=date_query) | Q(ending_date__icontains=date_query))
    if type_query:
        courses = courses.filter(Q(type__icontains=type_query))

    # Excluir cursos sin plazas disponibles y limitar a 6 cursos al final
    courses_with_images = [
        {
            **course.__dict__,
            'image_url': get_image_url(course.image),
            'available_slots': course.capacity - Reservation.objects.filter(course=course).exclude(paymentMethod='Pending').count()
        }
        for course in courses
        if course.capacity - Reservation.objects.filter(course=course).exclude(paymentMethod='Pending').count() > 0
    ][:6]

    context = {
        'courses': courses_with_images,
        'name_query': name_query,
        'type_query': type_query,
        'date_query': date_query,
        'type_choices': Course.TYPE_CHOICES
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
    reservas = Reservation.objects.filter(user=request.user, cart=False)
    cursos = [
        {
            **reserva.course.__dict__,
            'image_url': get_image_url(reserva.course.image),
            'available_slots': reserva.course.capacity - Reservation.objects
                            .filter(course=reserva.course).count(),
            'payment_status': 'Pendiente de pago' if reserva.paymentMethod ==
            'Pending' else 'Pagado'
        }
        for reserva in reservas
    ]

    return render(request, 'courses/my_courses.html', {'cursos': cursos})


def get_image_url(image):
    """
    Devuelve la URL completa de la imagen o la predeterminada si no hay imagen.
    """
    if image:
        return f"{settings.MEDIA_URL}{image}"
    return f"{settings.STATIC_URL}home/course_images/default_course_image.jpg"
