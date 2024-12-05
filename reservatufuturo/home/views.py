from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from .forms import EmailAuthenticationForm
from .models import Reservation, Course
from django.conf import settings
from django.utils import timezone
from django.db.models import Q, F
from django.contrib import messages
from django.contrib.auth.models import User, Group
from home.mail import enviar_notificacion_email
import stripe



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
    search = request.GET.get('search', '')
    
    user = request.user
    user_in_academy = user.groups.filter(name='academy').exists() if user.is_authenticated else False

    # Filtrar cursos
    if user_in_academy:
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(starting_date__gte=current_date)

    courses = courses.order_by('-starting_date')


    # Aplicar filtros
    if name_query:
        courses = courses.filter(Q(name__icontains=name_query))
    if date_query:
        courses = courses.filter(Q(starting_date__icontains=date_query) | Q(ending_date__icontains=date_query))
    if type_query:
        courses = courses.filter(Q(type__icontains=type_query))

    # Generar la lista base de cursos con imágenes y plazas disponibles
    courses_with_images = [
        {
            **course.__dict__,
            'image_url': get_image_url(course.image),
            'available_slots': max(0, course.capacity - Reservation.objects.filter(course=course).exclude(paymentMethod='Pending', cart=True).count())
        }
        for course in courses
    ]

    # Si no se ha realizado una búsqueda, excluir cursos sin plazas y limitar a 6
    if not (name_query or type_query or date_query or search):
        courses_with_images = [
            course for course in courses_with_images
            if course['available_slots'] > 0
        ][:6]

    context = {
        'courses': courses_with_images,
        'name_query': name_query,
        'type_query': type_query,
        'date_query': date_query,
        'type_choices': Course.TYPE_CHOICES,
        'today': current_date
    }
    
    if user.is_authenticated:
        # Obtener las reservas que están en el carrito
        cart_reservations = Reservation.objects.filter(user=user, cart=True, paymentMethod='Pending')
        cart_item_count = cart_reservations.count()
        cart_course_ids = cart_reservations.values_list('course_id', flat=True)

        # Obtener los cursos ya inscritos
        enrolled_reservations = Reservation.objects.filter(user=user, cart=False).exclude(paymentMethod='Pending')
        enrolled_course_ids = enrolled_reservations.values_list('course_id', flat=True)

        pending_reservations = Reservation.objects.filter(user=user, cart=False, paymentMethod='Pending')
        pending_course_ids = pending_reservations.values_list('course_id', flat=True)

        context['cart_item_count'] = cart_item_count
        context['cart_courses'] = cart_reservations.annotate(name=F('course__name')).values('name')
        context['cart_course_ids'] = list(cart_course_ids)
        context['enrolled_course_ids'] = list(enrolled_course_ids)
        context['pending_course_ids'] = list(pending_course_ids)
    else:
        context['cart_item_count'] = 0
        context['cart_courses'] = []
        context['cart_course_ids'] = []
        context['enrolled_course_ids'] = []
        context['pending_course_ids'] = []

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
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    reservas = Reservation.objects.filter(user=request.user, cart=False)
    cursos = [
        {
            **reserva.course.__dict__,
            'image_url': get_image_url(reserva.course.image),
            'available_slots': max(0, reserva.course.capacity - Reservation.objects.filter(
                course_id=reserva.course.id
            ).exclude(paymentMethod='Pending', cart=True).count()),
            'payment_status': 'Pendiente de pago' if reserva.paymentMethod ==
            'Pending' else 'Pagado'
        }
        for reserva in reservas
    ]

    return render(request, 'courses/my_courses.html', {'cursos': cursos, 'stripe_publishable_key': stripe_publishable_key})


def get_image_url(image):
    """
    Devuelve la URL completa de la imagen o la predeterminada si no hay imagen.
    """
    if image:
        return f"{settings.MEDIA_URL}{image}"
    return f"{settings.STATIC_URL}home/course_images/default_course_image.jpg"


def is_in_academy_group(user):
    return user.groups.filter(name='academy').exists()


def manage_users(request):
    if not request.user.is_authenticated or not is_in_academy_group(request.user):
        return redirect('homepage')
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user_to_delete = get_object_or_404(User, id=user_id)
        # Verificar que el usuario no pertenece al grupo 'academy'
        if not user_to_delete.groups.filter(name='academy').exists():
            try:
                destinatario = user_to_delete.email
                subject = "Eliminación de tu cuenta en ReservaTuFuturo"
                message = f"Hola {user_to_delete.first_name},\n\n"
                message += "Lamentamos informarte que tu cuenta en ReservaTuFuturo ha sido eliminada.\n\n"
                message += "Si tienes alguna duda o crees que esto es un error, puedes escribirnos a reservatufuturo@gmx.com o llamarnos al +34 123 456 789.\n\n"
                message += "Atentamente,\nEquipo de ReservaTuFuturo."
                enviar_notificacion_email(destinatario, subject, message)
                
                user_to_delete.delete()
                messages.success(request, f'El usuario "{user_to_delete.username}" ha sido eliminado correctamente.')
            except Exception as e:
                messages.error(request, f'Error al eliminar el usuario: {e}')
        else:
            messages.error(request, 'No puedes eliminar a un usuario que pertenece al grupo "academy".')
        return redirect('manage_users')

    # Obtener usuarios que no están en el grupo 'academy'
    academy_group = Group.objects.get(name='academy')
    users = User.objects.exclude(groups=academy_group).exclude(is_superuser=True).order_by('-date_joined')
    context = {
        'users': users
    }
    return render(request, 'home/manage_users.html', context)
