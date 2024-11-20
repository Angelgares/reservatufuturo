from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from .models import Course
from django.contrib.auth.decorators import login_required
from home.models import Reservation


class CourseListView(generic.ListView):
    modle = Course
    context_object_name = "courses_list"
    queryset = Course.objects.all()


class CourseDetailView(generic.DetailView):
    model = Course
    context_object_name = "course"
    template_name = "courses/course_detail.html"


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
