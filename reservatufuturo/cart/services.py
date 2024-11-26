from home.models import Reservation
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from courses.models import Course
from django.contrib import messages
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from home.mail import enviar_notificacion_email

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def remove_from_cart(request, reservation_id):
    # Obtener la reserva por ID y asegurar que pertenece al usuario autenticado
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user, cart=True)

    # Eliminar la reserva del carrito
    reservation.delete()
    
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


@login_required
@csrf_exempt
def checkout(request):
    try:
        # Calcular el total del carrito
        total_price = sum(
            reservation.course.price for reservation in Reservation.objects.filter(user=request.user, cart=True)
        )
        
        # Crear una sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": "Cesta de la compra",
                        },
                        "unit_amount": int(total_price * 100),  # Convertir a céntimos
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8000/cart/success/",
            cancel_url="http://localhost:8000/cart/cancel/",
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)})
    
@login_required
def payment_success(request):
    # Actualiza las reservas en el carrito del usuario
    reservations = Reservation.objects.filter(user=request.user, cart=True)
    reservations.update(cart=False, paymentMethod="Online")  # Actualiza el estado a "pagado"

    # Renderiza la plantilla de éxito
    return render(request, "cart/payment_success.html")

def quick_payment_success(request):

    return render(request, "cart/payment_success.html")

def payment_cancel(request):
    return render(request, "cart/payment_cancel.html")

def cash(request):
    # Actualiza las reservas en el carrito del usuario
    reservations = Reservation.objects.filter(user=request.user, cart=True)
    reservations.update(cart=False, paymentMethod="Cash")  # Actualiza el estado a "pagado"

    # Renderiza la plantilla de éxito
    return render(request, "cart/cash_success.html")

def cash_success(request, course_id, email):
    course = get_object_or_404(Course, id=course_id)
    destinatario = email
    asunto = f"Reserva de curso {course.name}"
    mensaje = f"¡Hola! Has reservado el curso {course.name} con éxito. Recuerda pagar en efectivo en la oficina antes de la fecha de inicio."
    enviar_notificacion_email(destinatario, asunto, mensaje)
    return render(request, "cart/cash_success.html")