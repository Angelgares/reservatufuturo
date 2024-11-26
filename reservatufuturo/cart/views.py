from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from home.models import Reservation
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from courses.models import Course
from django.http import JsonResponse
from django.contrib import messages
from django import forms
import stripe
from home.mail import enviar_notificacion_email
from django.urls import reverse
from django.contrib.auth.decorators import login_required


stripe.api_key = settings.STRIPE_SECRET_KEY

# Vista para el carrito de compras
class CartView(LoginRequiredMixin, generic.TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener las reservas del usuario actual que están en el carrito
        reservations = Reservation.objects.filter(user=self.request.user, cart=True)

        # Calcular el precio total
        total_price = sum(reservation.course.price for reservation in reservations)

        # Añadir al contexto
        context["reservations"] = reservations
        context["total_price"] = total_price
        context["stripe_publishable_key"] = settings.STRIPE_PUBLISHABLE_KEY  # Clave pública de Stripe

        return context

# Formulario para la compra rápida
class QuickPurchaseForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico", widget=forms.EmailInput(attrs={"class": "form-control"}))

# Vista para la compra rápida (Stripe)
class QuickPurchaseView(View):
    template_name = "cart/quick_purchase.html"

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        return render(request, self.template_name, {
            "course": course,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        })

    def post(self, request, course_id):
        email = request.POST.get("email")
        course = get_object_or_404(Course, id=course_id)
        success_url = request.build_absolute_uri(reverse("cart:quick_success"))
        cancel_url = request.build_absolute_uri(reverse("cart:quick_cancel"))

        if not email:
            return render(request, self.template_name, {
                "course": course,
                "error": "Por favor, ingresa un correo válido.",
            })

        try:
            # Crear o actualizar una reserva basada en el correo electrónico
            reservation, created = Reservation.objects.get_or_create(
                course=course,
                email=email,
                defaults={"cart": False, "paymentMethod": "Online"}
            )

            if not created:
                reservation.paymentMethod = "Online"
                reservation.cart = False
                reservation.save()

            # Crear sesión de Stripe Checkout
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer_email=email,
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "product_data": {
                                "name": course.name,
                            },
                            "unit_amount": int(course.price * 100),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return JsonResponse({"id": session.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# Vista para la compra rápida en efectivo
class QuickCashPurchaseView(View):
    template_name = "cart/quick_purchase.html"

    def post(self, request, course_id):
        email = request.POST.get("email")
        course = get_object_or_404(Course, id=course_id)

        if not email:
            return JsonResponse({"error": "Por favor, ingresa un correo válido."}, status=400)

        try:
            # Crear o actualizar una reserva basada en el correo electrónico
            reservation, created = Reservation.objects.get_or_create(
                course=course,
                email=email,
                defaults={"cart": False, "paymentMethod": "Cash"}
            )

            if not created:
                reservation.paymentMethod = "Cash"
                reservation.cart = False
                reservation.save()

            # Redirigir a la página de éxito
            return JsonResponse({"success_url": f"/cart/cash/success/{course.id}/{email}"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

# Eliminar un curso del carrito
@login_required
def remove_from_cart(request, reservation_id):
    # Obtener la reserva por ID y asegurar que pertenece al usuario autenticado
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user, cart=True)

    # Eliminar la reserva del carrito
    reservation.delete()
    
    messages.success(request, f'El curso "{reservation.course.name}" ha sido eliminado del carrito.')

    # Redirigir al carrito
    return redirect('cart:cart')

# Añadir un curso al carrito
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

# Checkout y pago
@login_required
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
            success_url=request.build_absolute_uri(reverse("cart:success")),
            cancel_url=request.build_absolute_uri(reverse("cart:cancel")),
        )
        return JsonResponse({"id": session.id})
    except Exception as e:
        return JsonResponse({"error": str(e)})

# Acción después de un pago exitoso
@login_required
def payment_success(request):
    # Actualiza las reservas en el carrito del usuario
    reservations = Reservation.objects.filter(user=request.user, cart=True)
    reservations.update(cart=False, paymentMethod="Online")  # Actualiza el estado a "pagado"

    # Renderiza la plantilla de éxito
    return render(request, "cart/payment_success.html")

# Acción después de un pago cancelado
def payment_cancel(request):
    return render(request, "cart/payment_cancel.html")

# Acción para completar el pago en efectivo
def cash(request):
    # Actualiza las reservas en el carrito del usuario
    reservations = Reservation.objects.filter(user=request.user, cart=True)
    reservations.update(cart=False, paymentMethod="Cash")  # Actualiza el estado a "pagado"

    # Renderiza la plantilla de éxito
    return render(request, "cart/cash_success.html")

# Acción después de completar un pago en efectivo
def cash_success(request, course_id, email):
    course = get_object_or_404(Course, id=course_id)
    destinatario = email
    asunto = f"Reserva de curso {course.name}"
    mensaje = f"¡Hola! Has reservado el curso {course.name} con éxito. Recuerda pagar en efectivo en la oficina antes de la fecha de inicio."
    enviar_notificacion_email(destinatario, asunto, mensaje)
    return render(request, "cart/cash_success.html")

def quick_payment_success(request):
    return render(request, "cart/payment_success.html")