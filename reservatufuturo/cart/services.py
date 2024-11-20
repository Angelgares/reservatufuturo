from home.models import Reservation
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from courses.models import Course
from django.contrib import messages

@login_required
def remove_from_cart(request, reservation_id):
    # Obtener la reserva por ID y asegurar que pertenece al usuario autenticado
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    # Cambiar el estado del carrito a False (eliminar del carrito)
    reservation.cart = False
    reservation.save()
    
    messages.success(request, f'El curso "{reservation.course.name}" ha sido eliminado del carrito.')

    # Redirigir al carrito
    return redirect('cart:cart')

@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    reservation, created = Reservation.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={'cart': True, 'paymentMethod': 'Pending'}
    )

    if created:
        messages.success(request, f'El curso "{course.name}" ha sido añadido al carrito.')
    elif not reservation.cart:
        reservation.cart = True
        reservation.paymentMethod = 'Pending'
        reservation.save()
        messages.success(request, f'El curso "{course.name}" ha sido añadido al carrito.')
    else:
        messages.info(request, f'El curso "{course.name}" ya está en el carrito.')

    return redirect('cart:cart')