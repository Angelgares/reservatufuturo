from typing import Any
from django.shortcuts import redirect, get_object_or_404, render
from django.views import generic
from .models import Course
from django.contrib.auth.decorators import login_required, user_passes_test
from home.models import Reservation
from django.views import generic
from itertools import groupby
from operator import itemgetter
from .forms import CourseForm
from django.http import HttpResponseForbidden
from django.conf import settings
from django.db.models import Q

class CourseListView(generic.ListView):
    model = Course
    context_object_name = "courses_grouped"
    template_name = "courses/course_list.html"
    queryset = Course.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('search', '')
        # Obtener solo los campos necesarios para optimizar la consulta
        courses = Course.objects.all().values(
            'type', 'id', 'name', 'teacher', 'price', 'capacity', 'image'
        )
        
        filtered_courses = courses.filter(
            Q(name__icontains=search_query) |
            Q(teacher__icontains=search_query) |
            Q(type__icontains=search_query)
        )

        # Agrupar cursos por tipo
        grouped_courses = {}
        for key, group in groupby(filtered_courses.order_by('type'), key=itemgetter('type')):
            grouped_courses[key] = [
                {
                    **course,
                    # Asegúrate de incluir la URL completa de la imagen
                    'image_url': self.get_image_url(course['image']),
                }
                for course in group
            ]

        context['courses_grouped'] = grouped_courses
        context['search_query'] = self.request.GET.get('search', '')
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
            has_reservation = Reservation.objects.filter(
                user=user,
                course=self.object
            ).exists()
        else:
            user_in_academy = False
            has_reservation = False

        context['user_in_academy'] = user_in_academy
        context['has_reservation'] = has_reservation
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
@user_passes_test(lambda user: user.groups.filter(name='academy').exists())
def course_inscriptions(request, pk):
    if not request.user.groups.filter(name='academy').exists():
        return HttpResponseForbidden("No tienes permisos para acceder a esta página")
    
    course = get_object_or_404(Course, pk=pk)
    # Filtrar solo las reservas completadas
    inscriptions = Reservation.objects.filter(
        course=course, 
        paymentMethod__in=['Online', 'Cash']
    ).select_related('user')
    
    return render(request, 'courses/course_inscriptions.html', {
        'course': course,
        'inscriptions': inscriptions,
    })
