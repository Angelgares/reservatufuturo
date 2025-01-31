from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic, View
from home.models import Reservation
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from courses.models import Course
from django.http import JsonResponse, Http404
from django.contrib import messages
from django import forms
import stripe
from home.mail import enviar_notificacion_email
from django.urls import reverse
from django.contrib.auth.decorators import login_required


stripe.api_key = settings.STRIPE_SECRET_KEY

# Vista para el carrito de compras
from decimal import Decimal


class CartView(LoginRequiredMixin, generic.TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener las reservas del usuario actual que están en el carrito
        reservations = Reservation.objects.filter(user=self.request.user, cart=True)

        # Calcular el subtotal (solo precios de los cursos)
        subtotal_courses = sum(
            Decimal(reservation.course.price) for reservation in reservations
        )

        # Calcular el total de gastos de gestión
        total_management_fee = sum(
            reservation.management_fee for reservation in reservations
        )

        # Calcular el precio total incluyendo los gastos de gestión
        total_price = subtotal_courses + total_management_fee

        # Añadir al contexto
        context["reservations"] = reservations
        context["subtotal_courses"] = subtotal_courses
        context["total_management_fee"] = total_management_fee
        context["total_price"] = total_price
        context["stripe_publishable_key"] = (
            settings.STRIPE_PUBLISHABLE_KEY
        )  # Clave pública de Stripe

        return context


# Formulario para la compra rápida
class QuickPurchaseForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )


# Vista para la compra rápida (Stripe)
import uuid
from django.http import JsonResponse, HttpResponseNotFound


class QuickPurchaseView(View):
    template_name = "cart/quick_purchase.html"

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        management_fee = 5 if course.price <= 150 else 0
        total_price = course.price + management_fee
        return render(
            request,
            self.template_name,
            {
                "course": course,
                "management_fee": management_fee,
                "total_price": total_price,
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            },
        )

    def post(self, request, course_id):
        email = request.POST.get("email")
        course = get_object_or_404(Course, id=course_id)

        if not email:
            return render(
                request,
                self.template_name,
                {
                    "course": course,
                    "error": "Por favor, ingresa un correo válido.",
                },
            )

        try:
            # Calcular los gastos de gestión
            management_fee = 5 if course.price <= 150 else 0
            total_price = course.price + management_fee

            # Crear o actualizar una reserva basada en el correo electrónico
            reservation, created = Reservation.objects.get_or_create(
                course=course,
                email=email,
                defaults={
                    "cart": False,
                    "paymentMethod": "Pending",
                    "management_fee": management_fee,
                },
            )

            if not created:
                reservation.paymentMethod = "Pending"
                reservation.cart = False
                reservation.management_fee = management_fee

            reservation.save()

            success_url = request.build_absolute_uri(
                reverse(
                    "cart:quick_success",
                    kwargs={
                        "course_id": course.id,
                        "email": email,
                        "tracking_code": reservation.tracking_code,  # Generar un UUID para el tracking_code
                    },
                )
            )
            cancel_url = request.build_absolute_uri(reverse("cart:quick_cancel"))

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
                            "unit_amount": int(
                                total_price * 100
                            ),  # Precio total en céntimos
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
            return JsonResponse(
                {"error": "Por favor, ingresa un correo válido."}, status=400
            )

        try:
            # Calcular los gastos de gestión
            management_fee = 5 if course.price <= 150 else 0
            total_price = course.price + management_fee

            # Crear o actualizar una reserva basada en el correo electrónico
            reservation, created = Reservation.objects.get_or_create(
                course=course,
                email=email,
                defaults={
                    "cart": False,
                    "paymentMethod": "Pending",
                    "management_fee": management_fee,
                },
            )

            if not created:
                reservation.paymentMethod = "Pending"
                reservation.cart = False
                reservation.management_fee = management_fee
                reservation.save()

            # Redirigir a la página de éxito
            return JsonResponse(
                {
                    "success_url": f"/cart/cash/success/{course.id}/{email}/{reservation.tracking_code}"
                }
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


# Eliminar un curso del carrito
@login_required
def remove_from_cart(request, reservation_id):
    try:
        # Obtener la reserva por ID y asegurar que pertenece al usuario autenticado
        reservation = Reservation.objects.get(
            id=reservation_id, user=request.user, cart=True
        )
        course_name = reservation.course.name

        # Eliminar la reserva del carrito
        reservation.delete()

        messages.success(
            request, f'El curso "{course_name}" ha sido eliminado del carrito.'
        )

    except Reservation.DoesNotExist:
        messages.warning(request, "La reserva ya ha sido eliminada o no existe.")

    # Redirigir al carrito
    return redirect("cart:cart")


# Añadir un curso al carrito
@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Calcular los gastos de gestión
    management_fee = 5 if course.price <= 150 else 0

    reservation, created = Reservation.objects.get_or_create(
        user=request.user,
        course=course,
        defaults={
            "cart": True,
            "paymentMethod": "Pending",
            "management_fee": management_fee,
        },
    )

    if created:
        messages.success(
            request, f'El curso "{course.name}" ha sido añadido al carrito.'
        )
    else:
        # Actualizar los valores si ya existía
        reservation.cart = True
        reservation.paymentMethod = "Pending"
        reservation.management_fee = management_fee
        reservation.save()
        messages.success(
            request, f'El curso "{course.name}" ha sido añadido al carrito.'
        )

    return redirect("cart:cart")


# Checkout y pago
@login_required
def checkout(request):
    try:
        # Obtener las reservas del carrito
        reservations = Reservation.objects.filter(user=request.user, cart=True)
        total_price = sum(
            Decimal(reservation.course.price) + reservation.management_fee
            for reservation in reservations
        )

        # URLs de éxito y cancelación
        success_url = request.build_absolute_uri(reverse("cart:payment_success"))
        cancel_url = request.build_absolute_uri(reverse("cart:payment_cancel"))

        # Crear una sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": "Cesta de la compra"},
                        "unit_amount": int(total_price * 100),  # Convertir a céntimos
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
        print(f"Error en checkout: {e}")  # Depuración en consola
        return JsonResponse({"error": str(e)}, status=400)


# Acción después de un pago exitoso
@login_required
def payment_success(request):
    # Obtener las reservas que están en el carrito (que fueron pagadas)
    reservations = Reservation.objects.filter(user=request.user, cart=True)

    # Recoger los cursos que fueron comprados
    purchased_courses_ids = [reservation.course_id for reservation in reservations]
    purchased_courses = []
    for course_id in purchased_courses_ids:
        course = Course.objects.get(id=course_id)
        purchased_courses.append(course)

    # Enviar el correo con la lista de cursos
    destinatario = request.user.email
    subject = "Confirmación de compra en ReservaTuFuturo"
    message = f"Hola {request.user.first_name},\n\n"
    message += "Gracias por confiar en ReservaTuFuturo para tu formación.\n\n"
    message += "Has adquirido los siguientes cursos:\n"

    for course in purchased_courses:
        tasas = 5 if course.price <= 150 else 0
        message += f"- {course.name}\n"
        message += f"     - Precio: {course.price} €\n"
        message += f"     - Gastos de gestión: {tasas} €\n"
        message += f"     - Método de pago: Online\n"
        message += f"     - Estado: Pagado\n"
        message += f"     - Fecha de inicio: {course.starting_date}\n\n"

    message += "Puedes acceder a tus cursos en la sección 'Mis cursos' después de iniciar sesión en nuestra web (reservatufuturo.onrender.com).\n\n"
    message += "¡Esperamos que disfrutes de tus cursos!\n\n"
    message += "Atentamente,\nEquipo de ReservaTuFuturo."

    enviar_notificacion_email(destinatario, subject, message)

    # Actualizar las reservas en el carrito a 'pagado'
    reservations.update(
        cart=False, paymentMethod="Online"
    )  # Marca las reservas como pagadas

    # Renderizar la plantilla de éxito de pago
    return render(request, "cart/payment_success.html", {"courses": purchased_courses})


# Acción después de un pago cancelado
def payment_cancel(request):
    return render(request, "cart/payment_cancel.html")


# Acción para completar el pago en efectivo
def cash(request):
    # Actualiza las reservas en el carrito del usuario
    reservations = Reservation.objects.filter(user=request.user, cart=True)

    # Recoger los cursos que fueron comprados
    purchased_courses_ids = [reservation.course_id for reservation in reservations]
    purchased_courses = []
    for course_id in purchased_courses_ids:
        course = Course.objects.get(id=course_id)
        purchased_courses.append(course)

    # Enviar un correo de confirmación
    destinatario = request.user.email
    subject = "Confirmación de compra en ReservaTuFuturo"
    message = f"Hola {request.user.first_name},\n\n"
    message += "Gracias por confiar en ReservaTuFuturo para tu formación.\n\n"
    message += "Has adquirido los siguientes cursos:\n"

    for course in purchased_courses:
        tasas = 5 if course.price <= 150 else 0
        message += f"- {course.name}\n"
        message += f"     - Precio: {course.price} €\n"
        message += f"     - Gastos de gestión: {tasas} €\n"
        message += f"     - Método de pago: Efectivo\n"
        message += f"     - Estado: Pendiente de pago\n"
        message += f"     - Fecha de inicio: {course.starting_date}\n\n"

    message += "Recuerda que debes acudir físicamente a nuestro local para pagar el importe de la compra.\n\n"
    message += "Puedes acceder a tus cursos en la sección 'Mis cursos' después de iniciar sesión en nuestra web (reservatufuturo.onrender.com).\n\n"
    message += "¡Esperamos que disfrutes de tus cursos!\n\n"
    message += "Atentamente,\nEquipo de ReservaTuFuturo."

    enviar_notificacion_email(destinatario, subject, message)
    reservations.update(cart=False, paymentMethod="Pending")

    # Renderiza la plantilla de éxito
    return render(request, "cart/cash_success.html")


# Acción después de completar un pago en efectivo
def cash_success(request, course_id, email, tracking_code):
    course = get_object_or_404(Course, id=course_id)
    destinatario = email
    subject = "Confirmación de compra en ReservaTuFuturo"
    message = f"Gracias por confiar en ReservaTuFuturo para tu formación.\n\n"
    message += "Has adquirido los siguientes cursos:\n"
    tasas = 5 if course.price <= 150 else 0
    message += f"- {course.name}\n"
    message += f"     - Precio: {course.price} €\n"
    message += f"     - Gastos de gestión: {tasas} €\n"
    message += f"     - Método de pago: Efectivo\n"
    message += f"     - Estado: Pendiente de pago\n"
    message += f"     - Fecha de inicio: {course.starting_date}\n"
    message += f"     - Nº seguimiento: {tracking_code}\n\n"

    message += "Recuerda que debes acudir físicamente a nuestro local para pagar el importe de la compra.\n\n"
    message += "Puedes realizar un seguimiento de tus cursos en la sección 'Seguimiento' en nuestra web (reservatufuturo.onrender.com).\n\n"
    message += "¡Esperamos que disfrutes de tus cursos!\n\n"
    message += "Atentamente,\nEquipo de ReservaTuFuturo."
    enviar_notificacion_email(destinatario, subject, message)
    return render(request, "cart/cash_success.html")


from django.shortcuts import render, get_object_or_404
from home.models import Reservation
from courses.models import Course
from home.mail import enviar_notificacion_email


def quick_payment_success(request, course_id, email, tracking_code):
    course = get_object_or_404(Course, id=course_id)
    reservation = get_object_or_404(Reservation, tracking_code=tracking_code)

    destinatario = email
    subject = "Confirmación de compra en ReservaTuFuturo"
    message = f"Gracias por confiar en ReservaTuFuturo para tu formación.\n\n"
    message += "Has adquirido los siguientes cursos:\n"
    tasas = 5 if course.price <= 150 else 0
    message += f"- {course.name}\n"
    message += f"     - Precio: {course.price} €\n"
    message += f"     - Gastos de gestión: {tasas} €\n"
    message += f"     - Método de pago: Online\n"
    message += f"     - Estado: Pagado\n"
    message += f"     - Fecha de inicio: {course.starting_date}\n"
    message += f"     - Nº seguimiento: {tracking_code}\n\n"

    message += "Puedes realizar un seguimiento de tus cursos en la sección 'Seguimiento' en nuestra web (reservatufuturo.onrender.com).\n\n"
    message += "¡Esperamos que disfrutes de tus cursos!\n\n"
    message += "Atentamente,\nEquipo de ReservaTuFuturo."
    enviar_notificacion_email(destinatario, subject, message)

    # Actualizar la reserva a 'pagado'
    reservation.cart = False
    reservation.paymentMethod = "Online"
    reservation.save()

    return render(request, "cart/payment_success.html")


def tracking_form(request):
    return render(request, "cart/tracking_form.html")


def reservation_tracking(request, tracking_code):
    stripe_publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    if not tracking_code:
        raise Http404("Código de seguimiento no proporcionado.")

    reservation = get_object_or_404(Reservation, tracking_code=tracking_code)
    course = reservation.course
    context = {
        "reservation": reservation,
        "course": course,
        "available_slots": course.capacity
        - Reservation.objects.filter(course=course).count(),
    }
    return render(
        request, "cart/reservation_tracking.html", {"reservation": reservation, 'stripe_publishable_key': stripe_publishable_key}
    )


def pay_course(request, course_id):
    reservation = get_object_or_404(
        Reservation,
        course_id=course_id,
        user_id=request.user.id,
        cart=False,
        paymentMethod="Pending",
    )
    try:
        total_price = Decimal(reservation.course.price) + reservation.management_fee

        # URLs de éxito y cancelación
        success_url = request.build_absolute_uri(
            reverse(
                "cart:update_payment_success", kwargs={"reservation_id": reservation.id}
            )
        )
        cancel_url = request.build_absolute_uri(reverse("cart:payment_cancel"))

        # Crear una sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": "Curso"},
                        "unit_amount": int(total_price * 100),  # Convertir a céntimos
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
        print(f"Error en checkout: {e}")
        return JsonResponse({"error": str(e)}, status=400)


def update_payment_success(request, reservation_id):
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return HttpResponseNotFound("Reserva no encontrada")

    course = reservation.course
    
    if reservation.user is None:
        reservation.cart = False
        reservation.paymentMethod = "Online"
        reservation.save()
        return render(request, "cart/payment_success.html")
    
    user = reservation.user
    email = user.email
    
    # Crear el mensaje de correo electrónico
    destinatario = email
    subject = "Confirmación de compra en ReservaTuFuturo"
    message = f"Hola {user.first_name},\n\n"
    message += "Gracias por confiar en ReservaTuFuturo para tu formación.\n\n"
    message += "Has adquirido los siguientes cursos:\n"
    
    tasas = 5 if course.price <= 150 else 0
    message += f"- {course.name}\n"
    message += f"     - Precio: {course.price} €\n"
    message += f"     - Gastos de gestión: {tasas} €\n"
    message += f"     - Método de pago: Online\n"
    message += f"     - Estado: Pagado\n"
    message += f"     - Fecha de inicio: {course.starting_date}\n"
    message += "Puedes acceder a tus cursos en la sección 'Mis cursos' después de iniciar sesión en nuestra web (reservatufuturo.onrender.com).\n\n"    
    message += "¡Esperamos que disfrutes de tus cursos!\n\n"
    message += "Atentamente,\nEquipo de ReservaTuFuturo."
    
    # Enviar el correo electrónico
    enviar_notificacion_email(destinatario, subject, message)
    
    # Actualizar la reserva a 'pagado'
    reservation.cart = False
    reservation.paymentMethod = "Online"
    reservation.save()

    return render(request, "cart/payment_success.html")

def pay_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
    )
    try:
        total_price = Decimal(reservation.course.price) + reservation.management_fee

        # URLs de éxito y cancelación
        success_url = request.build_absolute_uri(
            reverse(
                "cart:update_payment_success", kwargs={"reservation_id": reservation_id}
            )
        )
        cancel_url = request.build_absolute_uri(reverse("cart:payment_cancel"))

        # Crear una sesión de Stripe Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {"name": "Curso"},
                        "unit_amount": int(total_price * 100),  # Convertir a céntimos
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
        print(f"Error en checkout: {e}")
        return JsonResponse({"error": str(e)}, status=400)
