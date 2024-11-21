from typing import Any
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from .models import Course
from django.contrib.auth.decorators import login_required
from home.models import Reservation
from django.views import generic
from itertools import groupby
from operator import itemgetter

class CourseListView(generic.ListView):
    model = Course
    context_object_name = "courses_grouped"
    queryset = Course.objects.all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        courses = Course.objects.all().values('type', 'id', 'name', 'teacher', 'price', 'capacity', 'image')
        grouped_courses = {}
        for key, group in groupby(courses.order_by('type'), key=itemgetter('type')):
            grouped_courses[key] = list(group)

        context['courses_grouped'] = grouped_courses
        return context



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
