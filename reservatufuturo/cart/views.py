from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from home.models import Reservation
from django.conf import settings  # Para acceder a las claves de configuración

class CartView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener las reservas del usuario actual que están en el carrito
        reservations = Reservation.objects.filter(user=self.request.user, cart=True)

        # Calcular el precio total
        total_price = sum(reservation.course.price for reservation in reservations)

        # Añadir al contexto
        context['reservations'] = reservations
        context['total_price'] = total_price
        context['stripe_publishable_key'] = settings.STRIPE_PUBLISHABLE_KEY  # Clave pública de Stripe

        return context

    
    
