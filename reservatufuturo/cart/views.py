from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from home.models import Reservation
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from courses.models import Course
from django.http import JsonResponse
import stripe
from django import forms
from django.urls import reverse
from home.mail import enviar_notificacion_email


stripe.api_key = settings.STRIPE_SECRET_KEY

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
        context["stripe_publishable_key"] = (
            settings.STRIPE_PUBLISHABLE_KEY
        )  # Clave pública de Stripe

        return context


class QuickPurchaseForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )



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
                
            # Enviar notificación por correo electrónico
            destinatario = email
            asunto = "Reserva de curso"
            mensaje = f"Has reservado el curso {course.name} con éxito. Por favor, paga en efectivo en la oficina antes de la fecha de inicio."
            enviar_notificacion_email(destinatario, asunto, mensaje)

            # Redirigir a la página de éxito
            return JsonResponse({"success_url": "/cart/cash/success/{0}/{1}".format(course_id, email)})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
