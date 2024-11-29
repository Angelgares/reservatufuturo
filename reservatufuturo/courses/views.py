from django.shortcuts import redirect, get_object_or_404, render
from django.views import generic
from .models import Course
from django.contrib.auth.decorators import login_required
from home.models import Reservation
from itertools import groupby
from operator import itemgetter
from .forms import CourseForm
from django.http import HttpResponseForbidden
from django.conf import settings
from django.db.models import Q, F
from django.contrib import messages
from home.mail import enviar_notificacion_email
from django.utils import timezone


class CourseListView(generic.ListView):
    model = Course
    context_object_name = "courses_grouped"
    template_name = "courses/course_list.html"
    queryset = Course.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name_query = self.request.GET.get('name_search', '')
        type_query = self.request.GET.get('type_search', '')
        date_query = self.request.GET.get('date_search', '')
        current_date = timezone.now().date()
        
        user = self.request.user
        user_in_academy = user.groups.filter(name='academy').exists()

        # Obtener solo los campos necesarios para optimizar la consulta
        if user_in_academy:
            courses = Course.objects.values(
                'id', 'name', 'price', 'image', 'teacher', 'capacity',
                'description', 'starting_date', 'ending_date', 'type'
            )
        else:
            courses = Course.objects.filter(starting_date__gte=current_date).values(
                'id', 'name', 'price', 'image', 'teacher', 'capacity',
                'description', 'starting_date', 'ending_date', 'type'
            )

        filtered_courses1 = courses.filter(
            Q(name__icontains=name_query)
        )

        filtered_courses2 = filtered_courses1.filter(
            Q(starting_date__icontains=date_query) |
            Q(ending_date__icontains=date_query)
        )

        filtered_courses3 = filtered_courses2.filter(
            Q(type__icontains=type_query)
        )
        
        # Agrupar cursos por tipo
        grouped_courses = {}
        for key, group in groupby(filtered_courses3.order_by('type'), key=itemgetter('type')):
            grouped_courses[key] = [
                {
                    **course,
                    'image_url': self.get_image_url(course['image']),
                    'available_slots': course['capacity'] - Reservation.objects.filter(
                        course_id=course['id']
                    ).exclude(paymentMethod='Pending', cart=True).count()
                }
                for course in group
            ]

        context['courses_grouped'] = grouped_courses
        context['search_query'] = self.request.GET.get('search', '')
        context['type_choices'] = Course.TYPE_CHOICES
        context['today'] = timezone.now().date()

        
        # Añadir información del carrito y cursos inscritos si el usuario está autenticado
        if user.is_authenticated:
            # Obtener las reservas que están en el carrito
            cart_reservations = Reservation.objects.filter(user=user, cart=True, paymentMethod='Pending')
            cart_item_count = cart_reservations.count()
            cart_course_ids = cart_reservations.values_list('course_id', flat=True)

            # Obtener los cursos ya inscritos
            enrolled_reservations = Reservation.objects.filter(user=user, cart=False).exclude(paymentMethod__in=['Pending'])
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

        return context

    def get_image_url(self, image):
        """
        Devuelve la URL completa de la imagen o la predeterminada si no hay imagen.
        """
        if image:
            return f"{settings.MEDIA_URL}{image}"
        return f"{settings.STATIC_URL}home/course_images/default_course_image.jpg"


class CourseDetailView(generic.DetailView):
    model = Course
    context_object_name = "course"
    template_name = "courses/course_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            user_in_academy = user.groups.filter(name='academy').exists()
            reservation = Reservation.objects.filter(
                user=user,
                course=self.object
            ).first()
            has_reservation = reservation is not None
        else:
            user_in_academy = False
            has_reservation = False
            reservation = None

        # Calcular las plazas disponibles
        reserved_count = Reservation.objects.filter(course=self.object)\
            .exclude(paymentMethod='Pending', cart=True).count()
        available_slots = self.object.capacity - reserved_count

        context['user_in_academy'] = user_in_academy
        context['has_reservation'] = has_reservation
        context['reservation'] = reservation
        context['available_slots'] = available_slots
        return context


@login_required
def add_to_cart(request, course_id):
    # Obtén el curso por su ID
    course = get_object_or_404(Course, id=course_id)

    # Verifica si ya existe una reserva para este curso y usuario en el carrito
    reservation, created = Reservation.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'cart': True, 'paymentMethod': 'Pending'}
    )

    # Si ya existe y no está en el carrito, actualiza el estado
    if not created and not reservation.cart:
        reservation.cart = True
        reservation.paymentMethod = 'Pending'
        reservation.save()

    # Redirige al carrito
    return redirect('cart')

@login_required
def create_course(request):
    if not request.user.groups.filter(name='academy').exists():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            Course.objects.create(
                name=form.cleaned_data["name"],
                price=form.cleaned_data["price"],
                image=form.cleaned_data["image"],
                teacher=form.cleaned_data["teacher"],
                capacity=form.cleaned_data["capacity"],
                description=form.cleaned_data["description"],
                starting_date=form.cleaned_data["starting_date"],
                ending_date=form.cleaned_data["ending_date"],
                type=form.cleaned_data["type"])
            
            return redirect('courses')
        else:
            return render(request, 'courses/create_course.html', {'form': form, 'error': "Formulario inválido"})
    return render(request, 'courses/create_course.html', {'form': CourseForm()})

def delete_course(request, pk):
    if not request.user.groups.filter(name='academy').exists():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")
    
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    return redirect('courses')

@login_required
def update_course(request, pk):
    if not request.user.groups.filter(name='academy').exists():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")
    
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            # Actualizar los campos manualmente
            course.name = form.cleaned_data['name']
            course.price = form.cleaned_data['price']
            if 'image' in request.FILES:
                course.image = request.FILES['image']
            course.teacher = form.cleaned_data['teacher']
            course.capacity = form.cleaned_data['capacity']
            course.description = form.cleaned_data['description']
            course.starting_date = form.cleaned_data['starting_date']
            course.ending_date = form.cleaned_data['ending_date']
            course.type = form.cleaned_data['type']
            course.save()
            
            return redirect('course_detail', pk=course.pk)
        else:
            return render(request, 'courses/update_course.html', {'form': form, 'course': course, 'error': "Formulario inválido"})

    # Poblar el formulario con los valores actuales del curso
    form = CourseForm(initial={
        'name': course.name,
        'price': course.price,
        'image': course.image,
        'teacher': course.teacher,
        'capacity': course.capacity,
        'description': course.description,
        'starting_date': course.starting_date,
        'ending_date': course.ending_date,
        'type': course.type,
    })
    return render(request, 'courses/update_course.html', {'form': form, 'course': course})

@login_required
def course_inscriptions(request, pk):
    if not request.user.groups.filter(name='academy').exists():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")
    
    course = get_object_or_404(Course, pk=pk)
    # Filtrar solo las reservas completadas
    inscriptions = Reservation.objects.filter(
        course=course,
        cart=False
    ).select_related('user')
    
    return render(request, 'courses/course_inscriptions.html', {
        'course': course,
        'inscriptions': inscriptions,
    })

def remove_user_from_course(request, course_id, inscription_id):
    if request.method == "POST":
        # Obtén el curso y la inscripción
        course = get_object_or_404(Course, id=course_id)
        inscription = get_object_or_404(Reservation, id=inscription_id)

        # Envía un correo al usuario antes de eliminar
        if inscription.user:
            destinatario = inscription.user.email
        else:
            destinatario = inscription.email
            
        asunto = "Eliminación de inscripción en ReservaTuFuturo"
        mensaje = f"Tu inscripción al curso {course.name} ha sido eliminada."
        mensaje += "\n\nPara más información, contacta con la academia."
        mensaje += "\n\nAtentamente,\nEquipo de ReservaTuFuturo."
        enviar_notificacion_email(destinatario, asunto, mensaje)

        # Elimina la inscripción
        inscription.delete()
        messages.success(request, f"La inscripción del usuario ha sido eliminada correctamente.")

    # Redirige de vuelta a la lista de inscritos
    return redirect('course_inscriptions', pk=course_id)

@login_required
def update_payment_method(request, course_id, inscription_id):
    # Verificar que el usuario pertenece al grupo 'academy'
    if not request.user.groups.filter(name='academy').exists():
        return HttpResponseForbidden("No tienes permisos para realizar esta acción")

    # Obtener la inscripción
    inscription = get_object_or_404(Reservation, id=inscription_id, course_id=course_id)

    # Actualizar el método de pago
    if inscription.paymentMethod == 'Pending':
        inscription.paymentMethod = 'Cash'
        inscription.save()
        messages.success(request, f"El método de pago para {inscription.user or inscription.email} ha sido actualizado a 'Cash'.")
    else:
        messages.warning(request, f"El método de pago no se puede actualizar porque no está en estado 'Pending'.")

    # Redirigir de vuelta a la lista de inscritos
    return redirect('course_inscriptions', pk=course_id)
